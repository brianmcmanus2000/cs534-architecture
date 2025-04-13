#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <nlohmann/json.hpp> // JSON parser library: https://github.com/nlohmann/json
#include "booksim_wrapper.hpp" // Ensure this path is correct for your BookSim build

using json = nlohmann::json;
using namespace Booksim;

// Struct to store packet data
struct Packet {
    int timestamp;
    int source;
    int destination;
    int size;
};

// Function to load traffic data from JSON file
std::vector<Packet> load_traffic(const std::string& filename) {
    std::vector<Packet> traffic_data;
    std::ifstream file(filename);
    
    if (!file.is_open()) {
        std::cerr << "Error opening file: " << filename << std::endl;
        return traffic_data;
    }

    json traffic_json;
    file >> traffic_json;
    file.close();

    for (const auto& packet : traffic_json) {
        traffic_data.push_back({
            packet["timestamp"],
            packet["source"],
            packet["destination"],
            packet["size"]
        });
    }

    return traffic_data;
}

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <booksim_config_file> <traffic_file.json>" << std::endl;
        return 1;
    }

    std::string config_file = argv[1];
    std::string traffic_file = argv[2];

    // Load traffic data
    std::vector<Packet> traffic_data = load_traffic(traffic_file);
    if (traffic_data.empty()) {
        std::cerr << "No packets loaded from " << traffic_file << std::endl;
        return 1;
    }

    // Initialize BookSim
    BooksimWrapper booksim(config_file);

    std::cout << "Injecting packets..." << std::endl;

    // Simulate the network with injected traffic
    for (const auto& packet : traffic_data) {
        std::cout << "Injecting packet: Source=" << packet.source
                  << " Destination=" << packet.destination
                  << " Size=" << packet.size
                  << " Timestamp=" << packet.timestamp << std::endl;

        int packet_id = booksim.GeneratePacket(packet.source, packet.destination, packet.size, 0, packet.timestamp);
        
        if (packet_id == -1) {
            std::cerr << "Failed to inject packet from " << packet.source << " to " << packet.destination << std::endl;
        } else {
            std::cout << "Packet ID " << packet_id << " injected successfully." << std::endl;
        }
        
        booksim.RunCycles(10); // Run 10 cycles after each injection
    }

    // Retrieve completed packets
    std::cout << "Processing completed packets..." << std::endl;
    
    int cycles = 0;
    while (booksim.CheckInFlightPackets()) {
        std::cout << "Cycle " << cycles << ": Checking for completed packets..." << std::endl;
        Booksim::BooksimWrapper::RetiredPacket p = booksim.RetirePacket();
        
        if (p.pid != -1) {
            std::cout << "Packet " << p.pid << " completed, latency: " << p.plat 
                      << " cycles, hops: " << p.hops << std::endl;
        }
        
        booksim.RunCycles(10); // Run additional cycles until all packets are retired
        cycles += 10;

        // Prevent infinite loops
        if (cycles > 100000) {
            std::cerr << "Error: Simulation stuck, exceeding 100000 cycles." << std::endl;
            break;
        }
    }

    std::cout << "Simulation complete. Total cycles run: " << cycles << std::endl;
    return 0;
}
