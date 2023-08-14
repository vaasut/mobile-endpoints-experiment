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
    "os_image", "Disk Image", portal.ParameterType.STRING,
    COTS_UE_IMG,
    longDescription="File system image for the node."
)

pc.defineParameter(
    name="enable_novnc",
    description="enable noVNC",
    typ=portal.ParameterType.BOOLEAN,
    defaultValue=True,
    advanced=True
)

pc.defineParameter(
    name="deploy_test_tools",
    description="Deploy test tools",
    typ=portal.ParameterType.BOOLEAN,
    defaultValue=False,
    advanced=True
)

pc.defineParameter(
    name="orch_host",
    description="Orchestrator Hostname",
    typ=portal.ParameterType.STRING,
    defaultValue="",
    longDescription="Hostname of the orch (Grafana/Loki) server",
    advanced=True
)

params = pc.bindParameters()

all_routes = request.requestAllRoutes()
all_routes.disk_image = params.os_image
if params.deploy_test_tools:
    all_routes.addService(
        pg.Execute(shell="bash", command="sudo /local/repository/bin/deploy_test_tools.sh {}".format(params.orch_host))
    )

if params.enable_novnc:
    all_routes.startVNC()

tour = ig.Tour()
tour.Description(ig.Tour.MARKDOWN, tourDescription)
tour.Instructions(ig.Tour.MARKDOWN, tourInstructions)
request.addTour(tour)

pc.printRequestRSpec(request)
