let dotenvLoaded = false;
try {
  // eslint-disable-next-line global-require
  const dotenv = require('dotenv');
  dotenv.config();
  dotenvLoaded = true;
} catch (error) {
  console.warn('dotenv package is not installed yet. Loading defaults.');
}

const port = process.env.FRONTEND_PORT || 3000;

console.log(`UGC Marketplace frontend ready on port ${port} (dotenv loaded: ${dotenvLoaded})`);
