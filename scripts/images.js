const sharp = require("sharp");
const fs = require("node:fs");
const path = require("node:path");

// Input and output directories
const inputDirectory = path.join(__dirname, "../webapp/static_src/img/");
const outputDirectory = path.join(__dirname, "../webapp/static_compiled/img/");

// Resizing constraints
const maxWidth = 1920;
const maxHeight = 1080;

// Ensure dirs exist
if (!fs.existsSync(outputDirectory)) {
  fs.mkdirSync(outputDirectory, { recursive: true });
}

// Get all files in the input directory
const files = fs.readdirSync(inputDirectory);

// Each file and apply compression
files.forEach((file) => {
  if (file.match(/\.(jpg|jpeg|png|gif)$/)) {
    sharp(`${inputDirectory}/${file}`)
      .resize(maxWidth, maxHeight, {
        fit: "inside",
        withoutEnlargement: true,
      })
      .jpeg({ quality: 80, progressive: true }) // Progressive JPEGs
      .webp({ quality: 80 }) // Convert to WebP format
      .toFile(`${outputDirectory}/${file}`, (err) => {
        if (err) {
          console.error(`Error processing ${file}: ${err}`);
        } else {
          console.log(`Advanced compression applied to ${file}`);
        }
      });
  }
});
