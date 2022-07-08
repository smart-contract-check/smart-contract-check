import inspect
import sys
from pkg_resources import iter_entry_points
from slither.detectors import all_detectors
from slither.detectors.abstract_detector import AbstractDetector
from slither.printers import all_printers
from slither.printers.abstract_printer import AbstractPrinter
from slither.slither import Slither
import logging
logging.getLogger("Detectors").propagate = False
logging.getLogger("CryticCompile").propagate = False
from dotenv import load_dotenv
import os

load_dotenv()



def get_slither_results(filename):
    sys.setrecursionlimit(1500)
    detectors, printers = get_detectors_and_printers()

    slither = Slither(
        filename,
        solc_solcs_select="0.8.13,0.8.12,0.8.11,0.8.10,0.8.9,0.8.8,0.8.7,0.8.6,0.8.5,0.8.4,0.8.3,0.8.2,0.8.1,0.8.0,0.7.6,0.7.5,0.7.4,0.7.3,0.7.2,0.7.1,0.7.0,0.6.9,0.6.8,0.6.7,0.6.6,0.6.5,0.6.4,0.6.3,0.6.2,0.6.12,0.6.11,0.6.10,0.6.1,0.6.0,0.5.9,0.5.8,0.5.7,0.5.6,0.5.5,0.5.4,0.5.3,0.5.2,0.5.17,0.5.16,0.5.15,0.5.14,0.5.13,0.5.12,0.5.11,0.5.10,0.5.1,0.5.0,0.4.9,0.4.8,0.4.7,0.4.6,0.4.5,0.4.4,0.4.3,0.4.26,0.4.25,0.4.24,0.4.23,0.4.22,0.4.21,0.4.20,0.4.2,0.4.19,0.4.18,0.4.17,0.4.16,0.4.15,0.4.14,0.4.13,0.4.12,0.4.11,0.4.10,0.4.1,0.4.0",
        etherscan_api_key=os.getenv('ETHERSCAN_API_KEY')
    )

    for d in detectors:
        slither.register_detector(d)

    detector_results = slither.run_detectors()
    detector_results = [x for x in detector_results if x]  # remove empty results
    detector_results = [item for sublist in detector_results for item in sublist]  # flatten
    detector_results = [x for x in detector_results if x['impact'] != 'Optimization' and x[
        'impact'] != 'Informational']  # remove optimization and informational

    return detector_results


def get_detectors_and_printers():
    """
    NOTE: This contains just a few detectors and printers that we made public.
    """

    detectors = [getattr(all_detectors, name) for name in dir(all_detectors)]
    detectors = [d for d in detectors if inspect.isclass(d) and issubclass(d, AbstractDetector)]

    printers = [getattr(all_printers, name) for name in dir(all_printers)]
    printers = [p for p in printers if inspect.isclass(p) and issubclass(p, AbstractPrinter)]

    # Handle plugins!
    for entry_point in iter_entry_points(group="slither_analyzer.plugin", name=None):
        make_plugin = entry_point.load()

        plugin_detectors, plugin_printers = make_plugin()

        detector = None
        if not all(issubclass(detector, AbstractDetector) for detector in plugin_detectors):
            raise Exception(
                "Error when loading plugin %s, is not a detector" % entry_point
            )
        printer = None
        if not all(issubclass(printer, AbstractPrinter) for printer in plugin_printers):
            raise Exception(
                "Error when loading plugin %s, is not a printer" % entry_point
            )

        # We convert those to lists in case someone returns a tuple
        detectors += list(plugin_detectors)
        printers += list(plugin_printers)

    return detectors, printers
