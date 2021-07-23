import logging
from datetime import datetime
from queue import Queue
from uuid import uuid4

from flask import Blueprint, jsonify, request
from marshmallow import EXCLUDE, ValidationError

from bfgg.aws import S3Bucket
from bfgg.config import Config
from bfgg.controller.actors.dynamodb_resource import DynamoTableInteractor
from bfgg.controller.actors.report_handler import ReportHandler
from bfgg.controller.api.api_schemas import (
    CloneSchema,
    GroupSchema,
    ResultsSchema,
    StartSchema,
    StopSchema,
)
from bfgg.controller.state import State
from bfgg.utils.helpers import create_or_empty_results_folder
from bfgg.utils.messages import (
    CLONE,
    GROUP,
    START_TEST,
    STOP_TEST,
    OutgoingMessageGrouped,
    OutgoingMessageTargeted,
)


def blueprint(
    config: Config,
    state: State,
    outgoing_queue: Queue,
    dynamodb: DynamoTableInteractor,
    s3_bucket: S3Bucket,
    logger=logging.getLogger(__name__),
) -> Blueprint:
    bp = Blueprint("root", __name__)
    bad_request = 400

    @bp.route("/clone", methods=["POST"])
    def clone():
        try:
            result = CloneSchema().load(request.get_json(force=True), unknown=EXCLUDE)
        except ValidationError as err:
            return jsonify(err.messages), 400
        repo = result["repo"]
        grp = result["group"]
        outgoing_queue.put(
            OutgoingMessageGrouped(
                CLONE, repo.encode("utf-8"), group=grp.encode("utf-8")
            )
        )
        return {"clone": "requested"}

    @bp.route("/start", methods=["POST"])
    def start():
        try:
            result = StartSchema().load(request.get_json(force=True), unknown=EXCLUDE)
        except ValidationError as err:
            return jsonify(err.messages), bad_request
        project = result["project"]
        test = result["testClass"]
        java_opts = result.get("javaOpts", "")
        grp = result["group"]
        test_id = str(uuid4())
        task = f"{test_id},{project},{test},{java_opts}".encode("utf-8")
        # TODO - if test already running, return error
        outgoing_queue.put(
            OutgoingMessageGrouped(START_TEST, task, group=grp.encode("utf-8"))
        )
        create_or_empty_results_folder(config.results_folder, grp)
        try:
            logger.info(
                f"Attempting to save test details: {test_id}, {project}, {test}, {java_opts}"
            )
            dynamodb.save_test_started(
                test_id, datetime.utcnow(), project, test, result.get("javaOpts", None)
            )
            logger.info("Saved details to dynamo")
        except Exception as e:
            logger.error(e)
            if hasattr(e, "response"):
                return {"error": e.response["Error"]["Message"]}, 500
            else:
                return {"error": "Something went wrong"}, 500
        return {"test": "requested"}

    @bp.route("/stop", methods=["POST"])
    def stop():
        try:
            result = StopSchema().load(request.get_json(force=True), unknown=EXCLUDE)
        except ValidationError as err:
            return jsonify(err.messages), bad_request
        grp = result["group"]
        outgoing_queue.put(
            OutgoingMessageGrouped(STOP_TEST, b"STOP", group=grp.encode("utf-8"))
        )
        return {"testStop": "requested"}

    @bp.route("/status", methods=["GET"])
    def status():
        current_state = state.current_agents_state_list()
        return jsonify(current_state)

    @bp.route("/results", methods=["POST"])
    def results():
        try:
            result = ResultsSchema().load(request.get_json(force=True), unknown=EXCLUDE)
        except ValidationError as err:
            return jsonify(err.messages), bad_request
        grp = result["group"]
        getter = ReportHandler(
            config.results_folder,
            config.gatling_location,
            s3_bucket,
            config.s3_region,
            grp,
            config.report_url_base,
        )
        url = getter.run()
        return {"Results": url}

    @bp.route("/group", methods=["POST"])
    def group():
        try:
            result = GroupSchema().load(request.get_json(force=True), unknown=EXCLUDE)
        except ValidationError as err:
            return jsonify(err.messages), 400
        new_group = result["group"]
        agents = result["agents"]
        outgoing_queue.put(
            OutgoingMessageTargeted(
                GROUP,
                new_group.encode("utf-8"),
                [agent.encode("utf-8") for agent in agents],
            )
        )
        return {"grouping": "requested"}

    @bp.route("/past-tests", methods=["GET"])
    def past_tests():
        try:
            res = dynamodb.get_all()
        except Exception as e:
            logger.error(e)
            if hasattr(e, "response"):
                return {"error": e.response["Error"]["Message"]}, 500
            else:
                return {"error": "Something went wrong"}, 500
        return jsonify(res)

    return bp
