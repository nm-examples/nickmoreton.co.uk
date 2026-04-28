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

const faviconSource = path.join(inputDirectory, "favicon.svg");
const imageTasks = [];

if (fs.existsSync(faviconSource)) {
  fs.copyFileSync(faviconSource, path.join(outputDirectory, "favicon.svg"));

  imageTasks.push(
    sharp(faviconSource)
      .resize(32, 32)
      .png()
      .toFile(path.join(outputDirectory, "favicon-32x32.png")),
    sharp(faviconSource)
      .resize(180, 180)
      .png()
      .toFile(path.join(outputDirectory, "apple-touch-icon.png")),
  );
}

// Each file and apply compression
files.forEach((file) => {
  if (file.match(/\.(jpg|jpeg|png|gif)$/)) {
    imageTasks.push(
      sharp(`${inputDirectory}/${file}`)
        .resize(maxWidth, maxHeight, {
          fit: "inside",
          withoutEnlargement: true,
        })
        .jpeg({ quality: 80, progressive: true }) // Progressive JPEGs
        .webp({ quality: 80 }) // Convert to WebP format
        .toFile(`${outputDirectory}/${file}`)
        .then(() => {
          console.log(`Advanced compression applied to ${file}`);
        }),
    );
  }
});

Promise.all(imageTasks).catch((err) => {
  console.error(`Error processing images: ${err}`);
  process.exitCode = 1;
});
