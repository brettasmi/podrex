import scrape_itunes as psi
import podrex_db as db
import time

def scrape():
    conn, cursor = db.connect_db()
    podcast_name, itunes_url = db.get_unprocessed_podcast(cursor)
    cursor.execute("UPDATE podcasts SET processed = 'in_progress' "
                   "WHERE itunes_url = (%s) ", [itunes_url])
    conn.commit()
    with open("scrape.log", "a") as log:
        scrape_success = False
        pm, pr, scrape_success = psi.get_podcast_reviews(podcast_name, itunes_url)
        if not scrape_success:
            log.write("{}  |  failure to scrape on {}\n"
                      .format(time.strftime("%Y-%m-%d %H:%M:%S",
                                            time.localtime()),
                              podcast_name))
            conn, cursor = db.connect_db()
            cursor.execute("UPDATE podcasts "
                   "SET processed = 'problem' "
                   "WHERE itunes_url = (%s) ",
                  [itunes_url])
            conn.commit()
            return None
        # metadata_success = db.update_metadata(pm, conn, cursor)
        # if not metadata_success:
        #     log.write("{}  |  failure to update metadata on {}\n"
        #               .format(time.strftime("%Y-%m-%d %H:%M:%S",
        #                                     time.localtime()), podcast_name))
        #     conn, cursor = db.connect_db()
        # conn.commit()
        for review in pr:
            review_success = False
            review_success = db.update_reviews(review, conn, cursor)
            if not review_success:
                log.write("{}  |  failure to update review on {}\n"
                          .format(time.strftime("%Y-%m-%d %H:%M:%S",
                                                time.localtime()), podcast_name))
                conn, cursor = db.connect_db()
        conn.commit()
        if review_success:# and metadata_success:
            log.write("{}  |  success on {}\n"
                      .format(time.strftime("%Y-%m-%d %H:%M:%S",
                                            time.localtime()), podcast_name))
if __name__ == "__main__":
    while True:
        scrape()
