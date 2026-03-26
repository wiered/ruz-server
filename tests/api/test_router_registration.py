"""Contract tests for API router registration."""


import pytest


from ruz_server.api import api_router


@pytest.mark.api
class TestApiRouterRegistration:
    def test_expected_prefixes_are_registered(self):
        paths = {route.path for route in api_router.routes}
        expected = {
            "/group/",
            "/user/",
            "/lecturer/",
            "/kind_of_work/",
            "/discipline/",
            "/auditorium/",
            "/lesson/",
        }
        assert expected.issubset(paths)

    def test_registered_route_tags_match_contract(self):
        route_tags = {
            route.path: set(route.tags)
            for route in api_router.routes
            if getattr(route, "tags", None)
        }

        assert route_tags["/group/"] == {"group"}
        assert route_tags["/user/"] == {"user"}
        assert route_tags["/lecturer/"] == {"lecturer"}
        assert route_tags["/kind_of_work/"] == {"kind_of_work"}
        assert route_tags["/discipline/"] == {"discipline"}
        assert route_tags["/auditorium/"] == {"auditorium"}
        assert route_tags["/lesson/"] == {"lesson"}
