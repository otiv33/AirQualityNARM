// SQLITE
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
var dateFormat = require('date-format');

class Connection {
  db = null;

  async _initDb(){
    this.db = await this._createDbConnection('./db/airQuality.sqlite', (err) => {
      if (err) {
        console.error(err.message);
      }
      console.log('Connected to the airQuality database.');
    });
  }
  _createDbConnection(filename) {
    return open({
        filename,
        driver: sqlite3.Database
    });
  }

  constructor() {
    this._initDb();
  }

  async getMeasurements() {
    try {
      let sql = `SELECT * FROM measurements`;
      const result = await this.db.all(sql)
      // Sort by id DESC
      return result.sort((a, b) => b.id - a.id);
    } catch (error) {
      console.log(error);
    }
  }

  getTimestamp() {
    return dateFormat.asString('yyyy-mm-dd hh:MM:ss', new Date());
  }

  insertArsoMeasurement(measurement, id){
    try {
      let sql = `INSERT INTO measurements_ARSO (merilno_mesto,datum_od,datum_do,so2,co,o3,no2,pm10,pm25,benzen,measurements_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)`;
      const values = [measurement['merilno_mesto'],
                      measurement['datum_od'],
                      measurement['datum_do'],
                      measurement['so2'],
                      measurement['co'],
                      measurement['o3'],
                      measurement['no2'],
                      measurement['pm10'],
                      measurement['pm2.5'],
                      measurement['benzen'],
                      id]
      this.db.run(sql, values);
    } catch (error) {
      console.log(error);
    }

  }

  // LOCAL MEASUREMENTS
  insertLocalMeasurement(measurement){
    const self = this;
    let sql = `INSERT INTO measurements (pm1,pm25,pm4,pm10,h,t,voc,nox,dateTime) VALUES (?,?,?,?,?,?,?,?,?)`;
    const values = [measurement['pm1'],
                    measurement['pm25'],
                    measurement['pm4'],
                    measurement['pm10'],
                    measurement['h'],
                    measurement['t'],
                    measurement['voc'],
                    measurement['nox'],
                    this.getTimestamp()]
    var res = this.db.run(sql, values);
    return new Promise(async (resolve, reject) => {
      res.then(function(result){
        resolve(result.lastID);
      });
    });
  }

  closeConnetion(){
    this.db.close();
  }
}
const connection = new Connection();

module.exports = connection;