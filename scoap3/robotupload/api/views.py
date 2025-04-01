import logging

from rest_framework.parsers import BaseParser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from scoap3.articles.permissions import IsSuperUserOrReadOnly
from scoap3.robotupload.util import parse_marcxml
from scoap3.tasks import import_to_scoap3

logger = logging.getLogger(__name__)


class RawXMLParser(BaseParser):
    media_type = "application/xml"

    def parse(self, stream, media_type=None, parser_context=None):
        data = stream.read().decode("utf-8")
        return data


class RobotUploadViewSet(ViewSet):
    permission_classes = [IsSuperUserOrReadOnly]
    parser_classes = [RawXMLParser]

    def create(self, request):
        parsed_marcxml = parse_marcxml(request.data)
        import_to_scoap3(parsed_marcxml, True)

        return Response(parsed_marcxml)
