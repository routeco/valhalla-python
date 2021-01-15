#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <boost/noncopyable.hpp>
#include <boost/optional.hpp>
#include <boost/property_tree/ptree.hpp>
#include <sstream>
#include <string>

#include "baldr/graphreader.h"
#include "baldr/rapidjson_utils.h"
#include "midgard/logging.h"
#include "midgard/util.h"
#include "mjolnir/util.h"
#include "tyr/actor.h"

namespace vm = valhalla::mjolnir;
namespace vb = valhalla::baldr;
namespace py = pybind11;

class PythonGraphReader : public vb::GraphReader {
public:
  PythonGraphReader(const boost::property_tree::ptree& pt) : vb::GraphReader(pt, nullptr) {
  }
  std::shared_ptr<const GraphReader::tile_extract_t>
  get_extract_instance(const boost::property_tree::ptree& pt) {
    std::shared_ptr<const GraphReader::tile_extract_t> tile_extract(
        new GraphReader::tile_extract_t(pt));
    return tile_extract;
  }
};

namespace {
static std::unique_ptr<valhalla::tyr::actor_t> actor = nullptr;

// statically set the config file and configure logging, throw if you never configured
// configuring multiple times is possible, e.g. to change service_limits
// TODO: make this threadsafe just in case its abused
const boost::property_tree::ptree& configure(const std::string& config_path = "",
                                             py::dict config = {},
                                             const std::string& tile_dir = "",
                                             const std::string& tile_extract = "",
                                             bool verbose = true) {
  static boost::property_tree::ptree pt;

  // only build config when called from binding's Configure!
  if (!config_path.empty()) {
    // create the config on the filesystem via python
    py::object create_config = py::module_::import("valhalla.config").attr("_create_config");
    bool changed = create_config(config_path, config, tile_dir, tile_extract, verbose).cast<bool>();
    try {
      // parse the config
      boost::property_tree::ptree temp_pt;
      rapidjson::read_json(config_path, temp_pt);
      pt = temp_pt;

      // configure logging
      boost::optional<boost::property_tree::ptree&> logging_subtree =
          pt.get_child_optional("loki.logging");
      if (logging_subtree) {
        auto logging_config = valhalla::midgard::ToMap<const boost::property_tree::ptree&,
                                                       std::unordered_map<std::string, std::string>>(
            logging_subtree.get());
        valhalla::midgard::logging::Configure(logging_config);
      }
    } catch (...) { throw std::runtime_error("Failed to load config from: " + config_path); }
    if (changed) {
      actor.reset(new valhalla::tyr::actor_t(pt, true));
    }
  }

  // if it turned out no one ever configured us we throw
  if (pt.empty()) {
    throw std::runtime_error("The service was not configured");
  }

  return pt;
}

void py_configure(const std::string& config_file,
                  py::dict config,
                  const std::string& tile_dir,
                  const std::string& tile_extract,
                  bool verbose) {
  configure(config_file, std::move(config), tile_dir, tile_extract, verbose);
}

bool py_build_tiles(const std::vector<std::string>& input_pbfs) {
  auto pt = configure();

  // confuses the tile builder otherwise
  pt.get_child("mjolnir").erase("tile_extract");
  pt.get_child("mjolnir").erase("tile_url");

  bool result = vm::build_tile_set(pt, input_pbfs, vm::BuildStage::kInitialize,
                                   vm::BuildStage::kCleanup, false);

  if (result) {
    actor.reset(new valhalla::tyr::actor_t(pt, true));
  }

  return result;
}
} // namespace

PYBIND11_MODULE(python_valhalla, m) {
  m.def("Configure", py_configure, py::arg("config_file"), py::arg("config") = py::dict(),
        py::arg("tile_dir") = "", py::arg("tile_extract") = "", py::arg("verbose") = true);

  m.def("Route", [](const std::string req) { return actor->route(req); });
  m.def("Locate", [](const std::string req) { return actor->locate(req); });
  m.def("OptimizedRoute", [](const std::string req) { return actor->optimized_route(req); });
  m.def("Matrix", [](const std::string req) { return actor->matrix(req); });
  m.def("Isochrone", [](const std::string req) { return actor->isochrone(req); });
  m.def("TraceRoute", [](const std::string req) { return actor->trace_route(req); });
  m.def("TraceAttributes", [](const std::string req) { return actor->trace_attributes(req); });
  m.def("Height", [](const std::string req) { return actor->height(req); });
  m.def("TransitAvailable", [](const std::string req) { return actor->transit_available(req); });
  m.def("Expansion", [](const std::string req) { return actor->expansion(req); });

  m.def("_BuildTiles", py_build_tiles);
}
