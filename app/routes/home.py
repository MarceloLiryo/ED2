from flask import Blueprint, render_template, request
from app.models.country import country_service

home_bp = Blueprint("home", __name__)


@home_bp.route("/", methods=["GET"])
def index():
    query_code = request.args.get("codigo", "").strip()
    itinerary_raw = request.args.get("roteiro", "").strip()

    coverage_result = None
    search_performed = False
    search_comparisons = 0

    if query_code:
        search_performed = True
        coverage_result = country_service.get_by_code(query_code)
        search_comparisons = country_service.get_instrumentation()["last_search_comparisons"]

    itinerary_result = None
    if itinerary_raw:
        itinerary_result = country_service.recommend_package_for_itinerary(itinerary_raw)

    countries = country_service.list_all()
    metrics = country_service.get_instrumentation()

    return render_template(
        "home.html",
        countries=countries,
        query_code=query_code.upper(),
        search_performed=search_performed,
        coverage_result=coverage_result,
        search_comparisons=search_comparisons,
        itinerary_raw=itinerary_raw.upper(),
        itinerary_result=itinerary_result,
        metrics=metrics,
    )
