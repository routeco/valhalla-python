#include "mjolnir/osmway.h"
#include "mjolnir/util.h"

#include <valhalla/midgard/logging.h>

namespace valhalla {
namespace mjolnir {

OSMWay::OSMWay()
    : noderef_index_(0),
      nodecount_(0) {
  osmwayid_ = 0; //shouldnt this be -1 (ie std::numeric_limits<uint64_t>::max())?

  ref_ = "";
  int_ref_ = "";

  name_ = "";
  name_en_ = "";
  alt_name_ = "";
  official_name_ = "";

  destination_ = "";
  destination_ref_ = "";
  destination_ref_to_ = "";
  junction_ref_ = "";

  bike_national_ref_ = "";
  bike_regional_ref_ = "";
  bike_local_ref_ = "";

  attributes_.v = {0};

  classification_.v = {0};

  speed_ = static_cast<unsigned char>(0.0f);
}

OSMWay::OSMWay(uint64_t id)
    : noderef_index_(0),
      nodecount_(0){

  osmwayid_ = id;

  ref_ = "";
  int_ref_ = "";

  name_ = "";
  name_en_ = "";
  alt_name_ = "";
  official_name_ = "";

  destination_ = "";
  destination_ref_ = "";
  destination_ref_to_ = "";
  junction_ref_ = "";

  bike_national_ref_ = "";
  bike_regional_ref_ = "";
  bike_local_ref_ = "";

  attributes_.v = {0};

  classification_.v = {0};

  speed_ = static_cast<unsigned char>(0.0f);
}

OSMWay::~OSMWay() {
}

/**
 * Set way id.
 */
void OSMWay::set_way_id(const uint64_t id) {
  osmwayid_ = id;
}

/**
 * Get the way id
 */
uint64_t OSMWay::way_id() const {
  return osmwayid_;
}

// Set the index into the node references
void OSMWay::set_noderef_index(const uint32_t idx) {
  noderef_index_ = idx;
}

// Get the index into the node references
uint32_t OSMWay::noderef_index() const {
  return noderef_index_;
}

// Set the number of nodes for this way.
void OSMWay::set_node_count(const uint32_t count) {
  if (count > kMaxNodesPerWay) {
    LOG_ERROR("Exceeded max nodes per way: " + std::to_string(count));
    nodecount_ = static_cast<uint16_t>(kMaxNodesPerWay);
  } else {
    nodecount_ = static_cast<uint16_t>(count);
  }
}
/**
 * Get the number of nodes for this way.
 */
uint32_t OSMWay::node_count() const {
  return nodecount_;
}

/**
 * Sets the speed in KPH.
 */
void OSMWay::set_speed(const float speed) {
  speed_ = static_cast<unsigned char>(speed + 0.5f);
}

/**
 * Gets the speed in KPH.
 */
float OSMWay::speed() const {
  return static_cast<float>(speed_);
}

/**
 * Set the ref.
 */
void OSMWay::set_ref(const std::string& ref) {
  ref_ = ref;
}

/**
 * Get the ref.
 */
const std::string& OSMWay::ref() const {
  return ref_;
}

/**
 * Set the int ref.
 */
void OSMWay::set_int_ref(const std::string& int_ref) {
  int_ref_ = int_ref;
}

/**
 * Get the int ref.
 */
const std::string& OSMWay::int_ref() const {
  return int_ref_;
}

/**
 * Set the name.
 */
void OSMWay::set_name(const std::string& name) {
  name_ = name;
}

/**
 * Get the name.
 */
const std::string& OSMWay::name() const {
  return name_;
}

/**
 * Set the name:en.
 */
void OSMWay::set_name_en(const std::string& name_en) {
  name_en_ = name_en;
}

/**
 * Get the name:en.
 */
const std::string& OSMWay::name_en() const {
  return name_en_;
}

/**
 * Set the alt name.
 */
void OSMWay::set_alt_name(const std::string& alt_name) {
  alt_name_ = alt_name;
}

/**
 * Get the alt name.
 */
const std::string& OSMWay::alt_name() const {
  return alt_name_;
}

/**
 * Set the official name.
 */
void OSMWay::set_official_name(const std::string& official_name) {
  official_name_ = official_name;
}

/**
 * Get the official name.
 */
const std::string& OSMWay::official_name() const {
  return official_name_;
}

/**
 * Set the destination.
 */
void OSMWay::set_destination(const std::string& destination) {
  destination_ = destination;
}

/**
 * Get the get_destination.
 */
const std::string& OSMWay::destination() const {
  return destination_;
}

/**
 * Set the destination_ref.
 */
void OSMWay::set_destination_ref(const std::string& destination_ref) {
  destination_ref_ = destination_ref;
}

/**
 * Get the destination_ref.
 */
const std::string& OSMWay::destination_ref() const {
  return destination_ref_to_;
}

/**
 * Set the destination_ref_to.
 */
void OSMWay::set_destination_ref_to(const std::string& destination_ref_to) {
  destination_ref_to_ = destination_ref_to;
}

/**
 * Get the destination ref to.
 */
const std::string& OSMWay::destination_ref_to() const {
  return destination_ref_to_;
}

/**
 * Set the junction_ref.
 */
void OSMWay::set_junction_ref(const std::string& junction_ref) {
  junction_ref_ = junction_ref;
}

/**
 * Get the junction ref.
 */
const std::string& OSMWay::junction_ref() const {
  return junction_ref_;
}

/**
 * Set the bike national ref.
 */
void OSMWay::set_bike_national_ref(const std::string& bike_national_ref) {
  bike_national_ref_ = bike_national_ref;
}

/**
 * Get the bike national ref.
 */
const std::string& OSMWay::bike_national_ref() const {
  return bike_national_ref_;
}

/**
 * Set the bike regional ref.
 */
void OSMWay::set_bike_regional_ref(const std::string& bike_regional_ref) {
  bike_regional_ref_ = bike_regional_ref;
}

/**
 * Get the bike regional ref.
 */
const std::string& OSMWay::bike_regional_ref() const {
  return bike_regional_ref_;
}

/**
 * Set the bike local ref.
 */
void OSMWay::set_bike_local_ref(const std::string& bike_local_ref) {
  bike_local_ref_ = bike_local_ref;
}

/**
 * Get the bike local ref.
 */
const std::string& OSMWay::bike_local_ref() const {
  return bike_local_ref_;
}

/**
 * Set auto forward flag.
 */
void OSMWay::set_auto_forward(const bool auto_forward) {
  attributes_.fields.auto_forward = auto_forward;
}

/**
 * Get the auto forward flag.
 */
bool OSMWay::auto_forward() const {
  return attributes_.fields.auto_forward;
}

/**
 * Set bike forward flag.
 */
void OSMWay::set_bike_forward(const bool bike_forward) {
  attributes_.fields.bike_forward = bike_forward;
}

/**
 * Get the bike forward flag.
 */
bool OSMWay::bike_forward() const {
  return attributes_.fields.bike_forward;
}

/**
 * Set auto backward flag.
 */
void OSMWay::set_auto_backward(const bool auto_backward) {
  attributes_.fields.auto_backward = auto_backward;
}

/**
 * Get the auto backward flag.
 */
bool OSMWay::auto_backward() const {
  return attributes_.fields.auto_backward;
}

/**
 * Set bike backward flag.
 */
void OSMWay::set_bike_backward(const bool bike_backward) {
  attributes_.fields.bike_backward = bike_backward;
}

/**
 * Get the bike backward flag.
 */
bool OSMWay::bike_backward() const {
  return attributes_.fields.bike_backward;
}

/**
 * Set destination only/private flag.
 */
void OSMWay::set_destination_only(const bool destination_only) {
  attributes_.fields.destination_only = destination_only;
}

/**
 * Get the destination only/private flag.
 */
bool OSMWay::destination_only() const {
  return attributes_.fields.destination_only;
}
/**
 * Set pedestrian flag.
 */
void OSMWay::set_pedestrian(const bool pedestrian) {
  attributes_.fields.pedestrian = pedestrian;
}

/**
 * Get the pedestrian flag.
 */
bool OSMWay::pedestrian() const {
  return attributes_.fields.pedestrian;
}
/**
 * Set no thru traffic flag.
 */
void OSMWay::set_no_thru_traffic(const bool no_thru_traffic) {
  attributes_.fields.no_thru_traffic;
}

/**
 * Get the no thru traffic flag.
 */
bool OSMWay::no_thru_traffic() const {
  return attributes_.fields.no_thru_traffic;
}

/**
 * Set oneway flag.
 */
void OSMWay::set_oneway(const bool oneway) {
  attributes_.fields.oneway = oneway;
}

/**
 * Get the oneway flag.
 */
bool OSMWay::oneway() const{
  return attributes_.fields.oneway;
}

/**
 * Set roundabout flag.
 */
void OSMWay::set_roundabout(const bool roundabout) {
  attributes_.fields.roundabout = roundabout;
}

/**
 * Get the roundabout flag.
 */
bool OSMWay::roundabout() const {
  return attributes_.fields.roundabout;
}
/**
 * Set ferry flag.
 */
void OSMWay::set_ferry(const bool ferry) {
  attributes_.fields.ferry = ferry;
}

/**
 * Get the ferry flag.
 */
bool OSMWay::ferry() const {
  return attributes_.fields.ferry;
}
/**
 * Set rail flag.
 */
void OSMWay::set_rail(const bool rail) {
  attributes_.fields.rail = rail;
}

/**
 * Get the rail flag.
 */
bool OSMWay::rail() const {
  return attributes_.fields.rail;
}

/**
 * Set the surface.
 */
void OSMWay::set_surface(const Surface surface) {
  attributes_.fields.surface = static_cast<uint8_t>(surface);
}

/**
 * Get the surface.
 */
Surface OSMWay::surface() const {
  return static_cast<Surface>(attributes_.fields.surface);
}

/**
 * Set the cycle lane.
 */
void OSMWay::set_cyclelane(const CycleLane cyclelane) {
  attributes_.fields.cycle_lane = static_cast<uint8_t>(cyclelane);
}

/**
 * Get the cycle lane.
 */
CycleLane OSMWay::cyclelane() const {
  return static_cast<CycleLane>(attributes_.fields.cycle_lane);
}

/**
 * Sets the number of lanes
 */
void OSMWay::set_lanes(const uint32_t lanes) {
  attributes_.fields.lanes = lanes;
}

/**
 * Get the number of lanes
 */
uint32_t OSMWay::lanes() const {
  return attributes_.fields.lanes;
}

/**
 * Set tunnel flag.
 */
void OSMWay::set_tunnel(const bool tunnel) {
  attributes_.fields.tunnel = tunnel;
}

/**
 * Get the tunnel flag.
 */
bool OSMWay::tunnel() const {
  return attributes_.fields.tunnel;
}
/**
 * Set toll flag.
 */
void OSMWay::set_toll(const bool toll) {
  attributes_.fields.toll = toll;
}

/**
 * Get the toll flag.
 */
bool OSMWay::toll() const {
  return attributes_.fields.toll;
}
/**
 * Set bridge flag.
 */
void OSMWay::set_bridge(const bool bridge) {
  attributes_.fields.bridge = bridge;
}

/**
 * Get the bridge flag.
 */
bool OSMWay::bridge() const {
  return attributes_.fields.bridge;
}

//Sets the bike network mask
void OSMWay::set_bike_network(const uint32_t bikenetwork) {
  attributes_.fields.bikenetwork = bikenetwork;
}

uint32_t OSMWay::bike_network() const {
  return attributes_.fields.bikenetwork;
}

/**
 * Set exit flag.
 */
void OSMWay::set_exit(const bool exit) {
  attributes_.fields.exit = exit;
}

/**
 * Get the exit flag.
 */
bool OSMWay::exit() const {
  return attributes_.fields.exit;
}

/**
 * Get the road class.
 */
RoadClass OSMWay::road_class() const {
  return static_cast<RoadClass>(classification_.fields.road_class);
}

/**
 * Set the road class.
 */
void OSMWay::set_road_class(const RoadClass roadclass) {
  classification_.fields.road_class = static_cast<uint8_t>(roadclass);
}

/**
 * Set the use.
 */
void OSMWay::set_use(const Use use) {
  classification_.fields.use = static_cast<uint8_t>(use);
}

/**
 * Get the use.
 */
Use OSMWay::use() const {
  return static_cast<Use>(classification_.fields.use);
}

/**
 * Set link flag.
 */
void OSMWay::set_link(const bool link) {
  classification_.fields.link = link;
}

/**
 * Get the link flag.
 */
bool OSMWay::link() const {
  return classification_.fields.link;
}

/**
 * Get the names for the edge info based on the road class.
 */
std::vector<std::string> OSMWay::GetNames(const std::string& ref) const {
  std::vector<std::string> names;
  // Process motorway and trunk refs
  if ((!ref_.empty() || !ref.empty())
      && ((static_cast<RoadClass>(classification_.fields.road_class) == RoadClass::kMotorway)
          || (static_cast<RoadClass>(classification_.fields.road_class) == RoadClass::kTrunk))) {
    std::vector<std::string> tokens;

    if (!ref.empty())
      tokens = GetTagTokens(ref);// use updated refs from relations.
    else
      tokens = GetTagTokens(ref_);

    names.insert(names.end(), tokens.begin(), tokens.end());
  }

  // TODO int_ref

  // Process name
  if (!name_.empty())
    names.emplace_back(name_);

  // Process non limited access refs
  if (!ref_.empty() && (static_cast<RoadClass>(classification_.fields.road_class) != RoadClass::kMotorway)
      && (static_cast<RoadClass>(classification_.fields.road_class) != RoadClass::kTrunk)) {
    std::vector<std::string> tokens = GetTagTokens(ref_);
    names.insert(names.end(), tokens.begin(), tokens.end());
  }

  // Process alt_name
  if (!alt_name_.empty())
    names.emplace_back(alt_name_);

  // Process official_name
  if (!official_name_.empty())
    names.emplace_back(official_name_);

  // Process name_en_
  // TODO: process country specific names
  if (!name_en_.empty())
    names.emplace_back(name_en_);

  return names;
}

}
}
