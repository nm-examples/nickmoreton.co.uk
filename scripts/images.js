const sharp = require("sharp");
const fs = require("node:fs/promises");
const path = require("node:path");

const inputDirectory = path.join(__dirname, "../webapp/static_src/img");
const outputDirectory = path.join(__dirname, "../webapp/static_compiled/img");

async function buildImages() {
  await fs.mkdir(outputDirectory, { recursive: true });
  const files = await fs.readdir(inputDirectory);
  await Promise.all(
    files.map(async (file) => {
      const source = path.join(inputDirectory, file);
      if (/\.(svg|webp)$/i.test(file)) {
        await fs.copyFile(source, path.join(outputDirectory, file));
      } else if (/\.(jpe?g|png|gif)$/i.test(file)) {
        const output = `${path.parse(file).name}.webp`;
        await sharp(source)
          .resize(1920, 1080, { fit: "inside", withoutEnlargement: true })
          .webp({ quality: 80 })
          .toFile(path.join(outputDirectory, output));
      }
    }),
  );
  if (files.includes("favicon.svg")) {
    const favicon = path.join(inputDirectory, "favicon.svg");
    await Promise.all([
      sharp(favicon)
        .resize(32, 32)
        .png()
        .toFile(path.join(outputDirectory, "favicon-32x32.png")),
      sharp(favicon)
        .resize(180, 180)
        .png()
        .toFile(path.join(outputDirectory, "apple-touch-icon.png")),
    ]);
  }
}

buildImages().catch((error) => {
  console.error(`Error processing images: ${error}`);
  process.exitCode = 1;
});
