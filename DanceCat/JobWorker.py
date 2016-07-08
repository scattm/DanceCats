from Helpers import Timer
from DanceCat.DatabaseConnector import DatabaseConnector, DatabaseConnectorException


def job_worker(job_id, tracker_id):
    """
    For now only focus on execute and save results to redis.
    TODO:
     - will focus on trunking for better performance.
     - better error tracking
    :param job_id: Job object create from Model.Job
    :param tracker_id: Job Tracker for tracking job status
    :return: query result
    """
    timer = Timer()
    print "Begin executing job %d with tracker %d" % (job_id, tracker_id)

    from Models import Job, TrackJobRun
    from DanceCat import db

    job = Job.query.get(job_id)

    tracker = TrackJobRun.query.get(tracker_id)
    tracker.start()
    db.session.commit()

    try:
        db_connector = DatabaseConnector(
            job.Connection.type,
            job.Connection.db_config_generator(),
            sql_data_type=False,
            dict_format=False,
            timeout=120
        )

        db_connector.connect()
        db_connector.execute(job.queryString)
        results_header = db_connector.columns_name
        results_rows = db_connector.fetch_all()

        tracker.complete(
            is_success=True,
            run_duration=timer.get_total_milliseconds()
        )
        db.session.commit()

        return {
            'header': results_header,
            'rows': results_rows
        }

    except DatabaseConnectorException as e:
        tracker.complete(
            is_success=False,
            run_duration=timer.get_total_milliseconds(),
            error_string=e.message
        )
        db.session.commit()

    except Exception as e:
        tracker.complete(
            is_success=False,
            run_duration=timer.get_total_milliseconds(),
            error_string=e.message
        )
        db.session.commit()

    return None