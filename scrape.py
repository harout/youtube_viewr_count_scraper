import requests
import re
from multiprocessing import Pool
from datetime import datetime
from datetime import date
import glob
import json
import sqlite3
import time
import os


def fetch_channel_info(channel):
    channel_name = channel['name']
    channel_url = channel['url']
    channel_id = channel['id']

    page = requests.get(channel_url)
    print('Got results for ', channel_name)

    sub_count_search = re.search(
        r'subscriberCountText(.*?)"simpleText":"(.*?) subscribers"', page.text, re.M)
    num_subscribers = 0
    if sub_count_search:
        num_subscribers = sub_count_search.group(2)
        if num_subscribers.endswith('K'):
            num_subscribers = str(round(float(num_subscribers[:-1]) * 1000))
        num_subscribers = num_subscribers.replace(',', '')

    num_views_search = re.search(
        r'viewCountText(.*?)"simpleText":"(.*?) views"', page.text, re.M)
    if not num_views_search:
        return [channel_id, num_subscribers, 0]

    num_views = num_views_search.group(2)
    num_views = num_views.replace(',', '')
    return [channel_id, num_subscribers, num_views]


def get_url_to_channel_id_map(con):
    cur = con.cursor()
    cur.execute("SELECT url, id FROM channels")
    return dict((url, id) for url, id in cur.fetchall())


def get_available_report_dates(con):
    cur = con.cursor()
    cur.execute("""SELECT
                      DISTINCT captureDate
                   FROM
                      daily_data
                   ORDER BY
                      captureDate DESC""")
    date_list = [e[0] for e in cur.fetchall()]

    # All our deltas and the code computing them assume one report
    # per calendar day. Use the latest data for any given day if
    # more than one report exists.
    report_dates_seen = set()
    available_reports = []
    for date in date_list:
        key = timestamp_to_key(date)
        if key in report_dates_seen:
            print('Duplicate run on ', key)
            continue

        report_dates_seen.add(key)
        available_reports.append(date)

    available_reports.reverse()
    return available_reports


def timestamp_to_key(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%B_%d_%Y")


def split_list_to_batches(l, batch_size):
    return [l[i * batch_size:(i + 1) * batch_size]
            for i in range((len(l) + batch_size - 1) // batch_size)]


def correct_channel_view_counts(channelId, con):
    # First delete any duplicate captures
    cur = con.cursor()
    cur.execute("""SELECT 
                        DISTINCT strftime('%Y-%m-%d', datetime(captureDate, 'unixepoch')), 
                        captureDate 
                   FROM 
                        daily_data 
                   ORDER BY 
                        captureDate DESC""")

    captureDatesSeen = set()
    captureDatesToDelete = []
    for captureDateKey, captureDate in cur.fetchall():
        if captureDateKey in captureDatesSeen:
            captureDatesToDelete.append(captureDate)
        captureDatesSeen.add(captureDateKey)

    for captureDateToDelete in captureDatesToDelete:
        cur.execute("""DELETE FROM daily_data WHERE captureDate = ?""",
                    (captureDateToDelete,))
        con.commit()

    # Get the daily view counts for the channel
    cur.execute("""SELECT 
                        views,
                        captureDate 
                   FROM 
                        daily_data 
                   WHERE 
                        channelId = ? 
                   ORDER BY 
                        captureDate""", (channelId,))
    views = list([captureDate, views]
                 for views, captureDate in cur.fetchall())
    history = []

    # Itterate over the view counts. If we see a view count
    # that is less than the previous day's view count, then
    # we have work to do
    for date, view_count in views:
        if len(history) == 0:
            history.append([date, view_count])
            continue

        # If the view count is increasing, just keep
        # appending the view count to the history
        if history[-1][1] <= view_count:
            history.append([date, view_count])
            continue

        # We have encountered a view count that is lower than
        # the previous day's view count. All the view counts in
        # the history that are greater than this view count will
        # be thrown away. We will then lineary interpolate from
        # the last day with a lower count to today's count.
        suspect_dates = []
        while len(history) > 0 and history[-1][1] > view_count:
            suspect_dates.append(history.pop()[0])

        # If there is nothing good left in the history then
        # just copy today's view count back into the past
        if len(history) == 0:
            for date_from_history in suspect_dates:
                history.append([date_from_history, view_count])
            history.append([date, view_count])
            continue

        # We found a date in the history with a view count lower
        # than today's view count. We will not interpolate the
        # view count between these two values.
        start_date, start_count = history[-1]
        dt = date - start_date
        dc = view_count - start_count
        dc_dt = dc / dt

        for suspect_date in suspect_dates:
            dt = suspect_date - start_date
            dc = dc_dt * dt
            interpolated_count = int(start_count + dc)
            history.append([suspect_date, interpolated_count])

        history.append([date, view_count])

    for date, view_count in history:
        cur.execute("""UPDATE 
                            daily_data 
                       SET 
                            correctedViews = ? 
                       WHERE 
                            channelId = ? AND 
                            captureDate = ? 
                       LIMIT 1""", (view_count, channelId, date))
    con.commit()


def get_batch_data(dates, con):
    earliest_date = dates[0]
    latest_date = dates[-1]

    # Get all the distinct channel IDs in the specified
    # date range.
    cur = con.cursor()
    cur.execute("""SELECT
                      DISTINCT channelId
                   FROM
                      daily_data
                   WHERE
                      captureDate >= ? AND
                      captureDate <= ?""",
                (earliest_date, latest_date))
    channel_ids = [e[0] for e in cur.fetchall()]

    last_view_counts = {}
    last_subscriber_counts = {}

    for channel_id in channel_ids:
        cur.execute("""SELECT
                        correctedViews,
                        subscribers
                      FROM
                        daily_data
                      WHERE
                        captureDate < ? AND
                        channelId = ?
                      ORDER BY
                        captureDate DESC
                      LIMIT 1""", (earliest_date, channel_id))
        result = cur.fetchone()
        if result is None:
            last_view_counts[channel_id] = 0
            last_subscriber_counts[channel_id] = 0
        else:
            views, subscribers = result
            last_view_counts[channel_id] = views
            last_subscriber_counts[channel_id] = subscribers

    view_deltas = {}
    subscriber_deltas = {}
    subscriber_counts = {}
    for date in dates:
        key = timestamp_to_key(date)
        subscriber_counts[key] = {}
        subscriber_deltas[key] = {}
        view_deltas[key] = {}

        data = get_data_for_date(date, con)
        for channel_id, d in data.items():
            subscribers = d['subscribers']
            views = d['views']

            subscriber_counts[key][channel_id] = subscribers
            if channel_id in last_subscriber_counts:
                delta = subscribers - last_subscriber_counts[channel_id]
                subscriber_deltas[key][channel_id] = delta
            else:
                subscriber_deltas[key][channel_id] = subscribers

            if channel_id in last_view_counts:
                delta = views - last_view_counts[channel_id]
                view_deltas[key][channel_id] = delta
            else:
                view_deltas[key][channel_id] = views

            subscriber_counts[key][channel_id] = subscribers

            last_view_counts[channel_id] = views
            last_subscriber_counts[channel_id] = subscribers

    return view_deltas, subscriber_deltas, subscriber_counts


def write_batch_data_to_file(view_deltas,
                             subscriber_deltas,
                             subscriber_counts,
                             start,
                             end,
                             data_dir):
    prefix = timestamp_to_key(start) + '_' + timestamp_to_key(end)
    view_deltas_file_name = prefix + '.viewDeltas.json'
    subscriber_deltas_file_name = prefix + '.subscriberDeltas.json'
    subscriber_counts_file_name = prefix + '.subscriberCounts.json'

    fh = open(data_dir + view_deltas_file_name, 'w')
    fh.write(json.dumps(view_deltas, indent=2))
    fh.close()

    fh = open(data_dir + subscriber_deltas_file_name, 'w')
    fh.write(json.dumps(subscriber_deltas, indent=2))
    fh.close()

    fh = open(data_dir + subscriber_counts_file_name, 'w')
    fh.write(json.dumps(subscriber_counts, indent=2))
    fh.close()

    return view_deltas_file_name, subscriber_deltas_file_name, subscriber_counts_file_name


def get_data_for_date(date, con):
    cur = con.cursor()
    cur.execute("""SELECT
                      channelId,
                      correctedViews,
                      subscribers
                   FROM
                      daily_data
                   WHERE
                      captureDate = ?""", (date,))
    return dict((id, {'views': views, 'subscribers': subscribers})
                for id, views, subscribers in cur.fetchall())


def write_metadata_file(channels,
                        views_deltas_files,
                        subscriber_deltas_files,
                        subscriber_counts_files,
                        data_dir):
    meta = {}
    meta['channels'] = channels
    meta['viewDeltaFiles'] = views_deltas_files
    meta['subscriberDeltasFiles'] = subscriber_deltas_files
    meta['subscriberCountsFiles'] = subscriber_counts_files

    file_name = data_dir + 'metadata.json'
    fh = open(file_name, 'w')
    fh.write(json.dumps(meta, indent=2))
    fh.close()


def scrape_and_save_data(channels, con):
    now = int(time.time())
    cur = con.cursor()
    with Pool(3) as p:
        results = p.map(fetch_channel_info, channels.values())
        for result in results:
            channel_id = result[0]
            num_subscribers = result[1]
            num_views = result[2]
            data = (channel_id, num_views, num_subscribers, now)
            cur.execute("""INSERT INTO daily_data
                              (channelId,
                              views,
                              subscribers,
                              captureDate)
                            VALUES
                              (?, ?, ?, ?)""", data)
    con.commit()


def get_channels(con):
    cur = con.cursor()
    cur.execute("SELECT * FROM channels")
    return dict((id,
                {'id': id, 'name': name, 'url': url})
                for id, name, url in cur.fetchall())


if __name__ == '__main__':
    con = sqlite3.connect('./data/channel_stats.db')
    cur = con.cursor()
    channels = get_channels(con)

    scrape_and_save_data(channels, con)
    for channel in channels.values():
        correct_channel_view_counts(channel['id'], con)

    report_dates = get_available_report_dates(con)
    first_day, report_dates = report_dates[0], report_dates[1:]
    report_batches = split_list_to_batches(report_dates, 30)

    views_deltas_files = []
    subscriber_deltas_files = []
    subscriber_counts_files = []

    for batch in report_batches:
        batch_data = get_batch_data(batch, con)
        view_deltas, subscriber_deltas, subscriber_counts = batch_data
        start_key = timestamp_to_key(batch[0])
        end_key = timestamp_to_key(batch[-1])
        files = write_batch_data_to_file(view_deltas,
                                         subscriber_deltas,
                                         subscriber_counts,
                                         batch[0],
                                         batch[-1],
                                         './data/')
        views_deltas_files.append(
            {'fileName': files[0], 'start': start_key, 'end': end_key})
        subscriber_deltas_files.append(
            {'fileName': files[1], 'start': start_key, 'end': end_key})
        subscriber_counts_files.append(
            {'fileName': files[2], 'start': start_key, 'end': end_key})

    channels = get_channels(con)
    write_metadata_file(channels,
                        views_deltas_files,
                        subscriber_deltas_files,
                        subscriber_counts_files,
                        './data/')
    con.close()
