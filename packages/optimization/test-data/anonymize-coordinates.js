const fs = require("fs");
const path = require("path");

/**
 * Adds random jitter to lat/lng coordinates for anonymization
 * @param {number} coordinate - The original coordinate value
 * @param {number} jitterAmount - Maximum jitter in either direction (default ±0.001)
 * @returns {number} - Coordinate with added jitter
 */
function addJitter(coordinate, jitterAmount = 0.001) {
  // Generate random jitter between -jitterAmount and +jitterAmount
  const jitter = Math.random() * 2 * jitterAmount - jitterAmount;
  return parseFloat((coordinate + jitter).toFixed(7));
}

/**
 * Recursively processes an object to find and add jitter to lat/lng coordinates
 * @param {Object} obj - The object to process
 * @param {number} jitterAmount - Maximum jitter in either direction
 */
function processObject(obj, jitterAmount) {
  if (!obj || typeof obj !== "object") return;

  // If this is a geocodingResult with lat/lng, add jitter
  if (obj.lat !== undefined && obj.lng !== undefined) {
    obj.lat = addJitter(obj.lat, jitterAmount);
    obj.lng = addJitter(obj.lng, jitterAmount);
    return;
  }

  // Process all properties/elements of the object/array
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      processObject(obj[key], jitterAmount);
    }
  }
}

/**
 * Anonymizes coordinates in a JSON file
 * @param {string} inputFilePath - Path to input JSON file
 * @param {string} [outputFilePath] - Path for output file (defaults to input with "-anonymized" suffix)
 * @param {number} [jitterAmount] - Maximum jitter in either direction (default 0.001)
 */
function anonymizeCoordinates(
  inputFilePath,
  outputFilePath,
  jitterAmount = 0.001
) {
  // Read and parse the JSON file
  const jsonData = JSON.parse(fs.readFileSync(inputFilePath, "utf8"));

  // Process all objects in the data
  processObject(jsonData, jitterAmount);

  // Determine output path if not specified
  if (!outputFilePath) {
    const ext = path.extname(inputFilePath);
    const basePath = inputFilePath.slice(0, -ext.length);
    outputFilePath = `${basePath}-anonymized${ext}`;
  }

  // Write the modified JSON back to file
  fs.writeFileSync(outputFilePath, JSON.stringify(jsonData, null, 2));

  console.log(`Anonymized coordinates in ${inputFilePath}`);
  console.log(`Output written to ${outputFilePath}`);
}

// If run directly from command line
if (require.main === module) {
  if (process.argv.length < 3) {
    console.log(
      "Usage: node anonymize-coordinates.js <input-file> [output-file] [jitter-amount]"
    );
    process.exit(1);
  }

  const inputFile = process.argv[2];
  const outputFile = process.argv[3];
  const jitter = process.argv[4] ? parseFloat(process.argv[4]) : 0.001;

  anonymizeCoordinates(inputFile, outputFile, jitter);
}

module.exports = { anonymizeCoordinates, addJitter };
