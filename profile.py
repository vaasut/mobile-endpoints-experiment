import geni.portal as portal
import geni.rspec.igext as ig
import geni.rspec.pg as pg
import geni.rspec.emulab as emulab
import geni.rspec.emulab.route as route


tourDescription = """
### Mobile Endpoints for LTE/5G Experiments

POWDER provides a number of mobile endpoints deployed to university campus shuttles. In addition to other tools and SDRs, these mobile endpoints are equipped with LTE/5G modems that are capable of attaching to networks that include gNodeBs running at POWDER Dense Deployment sites.

This profile instantiates an exeriment that includes all of the currently available mobile endpoints traversing routes that come near one or more Dense Deployment sites. It is primarily intended to be run in conjunction with one of our outdoor 5G profiles:

- [OAI Outdoor 5G](https://www.powderwireless.net/show/PowderTeam/oai-outdoor-ota)
- [srsRAN Project Outdoor 5G](https://www.powderwireless.net/show/PowderTeam/srs-outdoor-ota)

**You'll need to instantiate one of these, or something similar, before you instantiate this profile if you want the UEs to attach to a 5G network.** In fact, in its default configuration, this profile will expect you to provide an `Orchestrator Hostname` in order to point a logging utility at an orchestration node deployed along with the rest of the resources in both of the outdoor 5G profiles. This hostname is provided in the instructions in the web UI of the outoor OAI or srsRAN experiment. (You can use this profile to deploy the mobile endpoints for other purposes too, of course.)

By default this profile installs and configures Promtail on each mobile endpoint to send logs to a Loki server running on the orchestrator along with some other useful tools in the form of system services, the logs for which Promtail is configured to monitor. These services include:

- `quectel-cm.service`: a connection manager that will attach the modem to the network and select a DNN/APN to connect to.
- `quectel-control.service`: mutiplexes communications to the serial interface of the UE in order to all multiple processes to talk to the modem's AT interface.
- `ue-metrics.service`: collects and send metrics to the orchestrator while the UE has a PDU session.
- `gpsd-client.service`: provides location information to the orchestrator.

Finally, it includes a terminal user interface (TUI) for the UE that allows a minimal set of commands to be sent to the modem via pressing keys on the keyboard. This is useful for debugging and for providing a way to interact with the modem without needing to use a serial console.

Note that mobile endpoints are ephemeral! Campus shuttles may come on route or go off route at any time. For this reason, the services listed above are started automatically. This way, if a new shuttle comes online, it will automatically start attaching to the network and start sending logs to the orchestrator. When a shuttle goes off route, the mobile endpoint will be terminated and the services will be stopped. We designed this profile to serve as a starting point with examples for pushing logs to an orchestrator in realtime so that data is not lost when the mobile endpoints are terminated.

"""

tourInstructions = """
### Instructions

1. **Start an Outdoor 5G Experiment**: Before you instantiate this profile, you should start an outdoor 5G experiment. You can use one of the following profiles: [OAI Outdoor 5G](https://www.powderwireless.net/show/PowderTeam/oai-outdoor-ota) or [srsRAN Project Outdoor 5G](https://www.powderwireless.net/show/PowderTeam/srs-outdoor-ota).

2. **Provide Orchestrator Hostname**: If you are using the default configuration, you will need to provide the hostname of the orchestrator that is running Loki. You can find this hostname in the web UI of the outdoor 5G experiment you just started.

3. **Set DNN**: You can set the DNN/APN that the connection manager will select for the UE. The default is `internet`, which corresponds to the default settings in the outdoor 5G profiles.

After that, as mobile endpoints come online, they will start attaching to the network and sending logs to the orchestrator, which you can explore using the corresponding Grafana server.

You can use the TUI to interact with the modem by running `/var/tmp/ue_app.py`. It provides an easy way to send the following commands to the modem:

- `A`: turn on airplane mode
- `U`: turn off airplane mode or turn on modem
- `D`: turn off modem
- `I`: check IMSI
- `S`: check serving cell metrics

"""

COTS_UE_IMG = "urn:publicid:IDN+emulab.net+image+PowderTeam:cots-jammy-image"

pc = portal.Context()
request = pc.makeRequestRSpec()

pc.defineParameter(
    name="deploy_test_tools",
    description="Deploy logging utility (Promtail) and some other useful UE tools.",
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
