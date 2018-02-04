#scrape_utils
import logging
import time
import urllib.request
import os
import podrex_db_utils as db

from scipy.stats import exponnorm


def get_art(conn, cursor):
    cursor.execute("select podcast_id, artwork from podcasts "
                   "where artwork is not null "
                   "and processed not in ('artwork', "
                   "'artwork_problem', 'getting_artwork') "
                   "limit 1")
    try:
        res = cursor.fetchone()
        if len(res)==0:
            return False, "db_fail", logging.exception()
    except:
        conn.rollback()
        return False, "db_fail", logging.exception()
    podcast_id = res[0]
    art_url = res[1]
    cursor.execute("update podcasts set processed = 'getting_artwork' "
                   "where podcast_id = (%s)", [podcast_id])
    file_extension_i = art_url.rfind(".")
    file_extension = art_url[file_extension_i:]
    try:
        urllib.request.urlretrieve(art_url,
                                   f"./artwork/{podcast_id}{file_extension}")
        cursor.execute("update podcasts "
                       "set processed = 'getting_artwork' "
                       "where podcast_id = (%s)", [podcast_id])
        return True, podcast_id, None
    except:
        return False, podcast_id, logging.exception()

def main():
    conn, cursor = db.connect_db()
    dir_check = os.path.exists("./artwork")
    if not dir_check:
        os.mkdir("./artwork")
    with open("art.log", "a") as logfile:
        while True:
            success, podcast_id, trace = get_art(conn, cursor)
            f_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            if not success:
                if podcast_id == "db_fail":
                    logfile.write(f"{f_time} | {trace}\n")
                    print(f"{f_time} | {trace}")
                    break
                else:
                    logfile.write(f"{f_time} | {trace}\n")
                    print(f"{f_time} | {trace}")
                    time.sleep(exponnorm.rvs(2, loc=22, scale=1, size=1))
            cursor.execute("update podcasts "
                           "set processed = 'artwork' "
                           "where podcast_id = (%s)", [podcast_id])
            logfile.write(f"{f_time} | Success on {podcast_id}\n")
            print(f"{f_time} | Success on {podcast_id}")
            time.sleep(exponnorm.rvs(2, loc=22, scale=1, size=1))
if __name__ == "__main__":
    main()
