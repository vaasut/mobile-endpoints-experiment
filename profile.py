import geni.portal as portal
import geni.rspec.igext as ig
import geni.rspec.pg as pg
import geni.rspec.emulab as emulab
import geni.rspec.emulab.route as route

tourDescription = """
### Instructions
### TODO ###
"""

tourInstructions = """
### Instructions
### TODO ###
"""

GR_IMAGE = 'urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-GR310'

pc = portal.Context()
request = pc.makeRequestRSpec()

pc.defineParameter(
    name="enable_novnc",
    description="Enable noVNC on each mobile endpoint.",
    typ=portal.ParameterType.BOOLEAN,
    defaultValue=True,
    advanced=True
)

params = pc.bindParameters()

all_routes = request.requestAllRoutes()
all_routes.disk_image = GR_IMAGE
all_routes.addService(
    pg.Execute(shell="bash", command="sudo /local/repository/bin/deploy_test_tools.sh")
)

if params.enable_novnc:
    all_routes.startVNC()

tour = ig.Tour()
tour.Description(ig.Tour.MARKDOWN, tourDescription)
tour.Instructions(ig.Tour.MARKDOWN, tourInstructions)
request.addTour(tour)

pc.printRequestRSpec(request)

