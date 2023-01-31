var express = require('express');
var router = express.Router();
const db = require('../db.js');

/* GET users listing. */
router.get('/', async function(req, res) {
  res.setHeader('Content-Type', 'application/json');
  const body = await db.getMeasurements();
  res.end(JSON.stringify(body));
});

/* GET users listing. */
router.post('/', function(req, res) {
  console.log('Received post req : '+JSON.stringify(req.body));
  db.insertMeasurement(req.body);
  res.json({ message: "Inserted measurement" });
});

module.exports = router;
