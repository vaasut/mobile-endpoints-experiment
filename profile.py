import geni.portal as portal
import geni.rspec.igext as ig
import geni.rspec.pg as pg
import geni.rspec.emulab as emulab
import geni.rspec.emulab.route as route


tourDescription = """
### General Mobile Endpoint Profile
"""

tourInstructions = """
### Instructions
"""

COTS_UE_IMG = "urn:publicid:IDN+emulab.net+image+PowderTeam:cots-jammy-image"

pc = portal.Context()
request = pc.makeRequestRSpec()

pc.defineParameter(
    name="deploy_test_tools",
    description="Deploy logging utility (Promtail)) and some other useful UE tools.",
    typ=portal.ParameterType.BOOLEAN,
    defaultValue=True
)

pc.defineParameter(
    name="orch_host",
    description="Orchestrator Hostname",
    typ=portal.ParameterType.STRING,
    defaultValue="",
    longDescription="Hostname of the orch (Grafana/Loki) server. Required if deploy_test_tools is enabled.",
)

pc.defineParameter(
    name="dnn",
    description="DNN/APN to connect to",
    typ=portal.ParameterType.STRING,
    defaultValue="internet",
    longDescription="DNN/APN that the connection manager will select for the UE."
)

pc.defineParameter(
    name="enable_novnc",
    description="Enable noVNC on each mobile endpoint.",
    typ=portal.ParameterType.BOOLEAN,
    defaultValue=True,
    advanced=True
)

pc.defineParameter(
    name="os_image",
    description="Disk Image",
    typ=portal.ParameterType.STRING,
    defaultValue=COTS_UE_IMG,
    longDescription="File system image for the node.",
    advanced=True
)

params = pc.bindParameters()

all_routes = request.requestAllRoutes()
all_routes.disk_image = params.os_image
if params.deploy_test_tools:
    all_routes.addService(
        pg.Execute(shell="bash", command="sudo /local/repository/bin/deploy_test_tools.sh {}".format(params.orch_host))
    )

all_routes.addService(
    pg.Execute(shell="bash", command="sudo /local/repository/bin/setup_cots_ue.sh {}".format(params.dnn))
)

if params.enable_novnc:
    all_routes.startVNC()

tour = ig.Tour()
tour.Description(ig.Tour.MARKDOWN, tourDescription)
tour.Instructions(ig.Tour.MARKDOWN, tourInstructions)
request.addTour(tour)

pc.printRequestRSpec(request)
