#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <algorithm>

extern "C" {
    int* bt_steps(char* filepath, char* filepath2);
}

using namespace std;

enum Direction {
    NONE = 0, // No movement (for the start of traceback)
    DIAGONAL = 1,
    UP = 2,
    LEFT = 3
};

const int MATCH_SCORE = 1;
const int MISMATCH_PENALTY = -1;
const int GAP_OPEN_PENALTY = -1;
const int GAP_EXTEND_PENALTY = -1;

std::string readNTSeq(const std::string& filepath) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << filepath << std::endl;
        return "";
    }

    std::string line, sequence;
    while (std::getline(file, line)) {
        sequence += line;
    }

    return sequence;
}

std::string hexToAscii(const std::string& hexStr) {
    std::string asciiStr;
    for (int i = hexStr.length()-2; i >=0 ; i -= 2) {
        std::string byteStr = hexStr.substr(i, 2);
        char byte = static_cast<char>(std::stoul(byteStr, nullptr, 16));
        asciiStr.push_back(byte);
    }
    return asciiStr;
}

std::string readHexFile(const std::string& filepath) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << filepath << std::endl;
        return "";
    }

    std::string line, result;
    while (std::getline(file, line)) {
        if (line.find("0x") == 0 || line.find("0X") == 0) {
            line = line.substr(2);  // Remove the "0x" prefix
            result += hexToAscii(line);
        }else{
            // result += 'N';
            // cout << result;
        }
    }

    return result;
}

int tracebackStepCount(const vector<vector<Direction>>& traceback, int i, int j) {
    int stepCount = 0;

    while (i > 0 && j > 0 && traceback[i][j] != NONE) {
        switch (traceback[i][j]) {
            case DIAGONAL:
                i--;
                j--;
                break;
            case UP:
                i--;
                break;
            case LEFT:
                j--;
                break;
            default:
                break;
        }
        stepCount++;
    }

    return stepCount;
}


int smithWatermanAffine(const string& a, const string& b) {
    int lenA = a.length();
    int lenB = b.length();

    vector<vector<int>> H(lenA + 1, vector<int>(lenB + 1, 0));
    vector<vector<int>> E(lenA + 1, vector<int>(lenB + 1, 0));
    vector<vector<int>> F(lenA + 1, vector<int>(lenB + 1, 0));
    vector<vector<Direction>> traceback(lenA + 1, vector<Direction>(lenB + 1, NONE));

    int maxScore = 0, maxI = 0, maxJ = 0;

    // Update this part to record direction
    for (int i = 1; i <= lenA; i++) {
        for (int j = 1; j <= lenB; j++) {

            E[i][j] = max(H[i][j-1] + GAP_OPEN_PENALTY, E[i][j-1] + GAP_EXTEND_PENALTY);
            F[i][j] = max(H[i-1][j] + GAP_OPEN_PENALTY, F[i-1][j] + GAP_EXTEND_PENALTY);
            int matchScore = 0;
            if (a[i-1] != 'N' && b[j-1] != 'N') {
                matchScore = a[i-1] == b[j-1] ? MATCH_SCORE : MISMATCH_PENALTY;
            }
            H[i][j] = max(0, max(H[i-1][j-1] + matchScore, max(E[i][j], F[i][j])));
            if (H[i][j] > maxScore) {
                maxScore = H[i][j];
                maxI = i;
                maxJ = j;
            }

            // Record direction
            if (H[i][j] == H[i-1][j-1] + matchScore) {
                traceback[i][j] = DIAGONAL;
            } else if (H[i][j] == E[i][j]) {
                traceback[i][j] = LEFT;
            } else if (H[i][j] == F[i][j]) {
                traceback[i][j] = UP;
            }
        }
    }
    int tb_steps = tracebackStepCount(traceback, maxI, maxJ);
    // cout << "Max Score: " << maxScore << " " << maxI << " " << maxJ << "\n";
    // cout << "Traceback Steps: " << tb_steps << "\n";
    return tb_steps;
}

// // Smith-Waterman algorithm with affine gap penalties
// void smithWatermanAffine(const string& a, const string& b) {
//     int lenA = a.length();
//     int lenB = b.length();

//     vector<vector<int>> H(lenA + 1, vector<int>(lenB + 1, 0));
//     vector<vector<int>> E(lenA + 1, vector<int>(lenB + 1, 0));
//     vector<vector<int>> F(lenA + 1, vector<int>(lenB + 1, 0));

//     int maxScore = 0, maxI = 0, maxJ = 0;

//     for (int i = 1; i <= lenA; i++) {
//         for (int j = 1; j <= lenB; j++) {
//             E[i][j] = max(H[i][j-1] + GAP_OPEN_PENALTY, E[i][j-1] + GAP_EXTEND_PENALTY);
//             F[i][j] = max(H[i-1][j] + GAP_OPEN_PENALTY, F[i-1][j] + GAP_EXTEND_PENALTY);
//             int matchScore = 0;
//             if (a[i-1] != 'N' && b[j-1] != 'N') {
//                 matchScore = a[i-1] == b[j-1] ? MATCH_SCORE : MISMATCH_PENALTY;
//             }
//             H[i][j] = max(0, max(H[i-1][j-1] + matchScore, max(E[i][j], F[i][j])));
//             if (H[i][j] > maxScore) {
//                 maxScore = H[i][j];
//                 maxI = i;
//                 maxJ = j;
//             }
//         }
//     }

//     cout << "Max Score: " << maxScore << " " << maxI <<" "  <<  maxJ << "\n";
//     cout << "Traceback Steps: " << tracebackStepCount(H, a, b, maxI, maxJ) << "\n";
// }

int* bt_steps(char* path_ref, char* path_query) {
    std::stringstream refss, queryss;
    refss << path_ref;
    queryss << path_query;
    string fileA = refss.str();
    string fileB = queryss.str();
    string sequenceA = readHexFile(fileA);
    string sequenceB = readHexFile(fileB);

    int steps = smithWatermanAffine(sequenceA, sequenceB);
    int* out = new int[3];
    out[0] = 320;
    out[1] = 320;
    out[2] = steps;

    return out;
}
