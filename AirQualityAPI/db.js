// SQLITE
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
var dateFormat = require('dateformat');

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
    return dateFormat(new Date(), "yyyy-mm-dd hh:MM:ss");
  }

  insertArsoMeasurement(measurement){
    let sql = `INSERT INTO measurements_ARSO (merilno_mesto,datum_od,datum_do,so2,co,o3,no2,pm10,pm25,benzen) VALUES (?,?,?,?,?,?,?,?,?,?)`;
    const values = [measurement['merilno_mesto'],
                    measurement['datum_od'],
                    measurement['datum_do'],
                    measurement['so2'],
                    measurement['co'],
                    measurement['o3'],
                    measurement['no2'],
                    measurement['pm10'],
                    measurement['pm25'],
                    measurement['benzen']]
    // this.db.run(sql, values);
    this.db.query(sql, values, function(err, result, fields) {
      if (err) throw err;
    
      var id = result.insertId;
      return id;
    });
  }

  insertLocalMeasurement(measurement, arso_measurement_id){
    let sql = `INSERT INTO measurements (pm1,pm25,pm4,pm10,h,t,voc,nox,dateTime) VALUES (?,?,?,?,?,?,?,?,?)`;
    const values = [measurement['pm1'],
                    measurement['pm25'],
                    measurement['pm4'],
                    measurement['pm10'],
                    measurement['h'],
                    measurement['t'],
                    measurement['voc'],
                    measurement['nox'],
                    this.getTimestamp(),
                    arso_measurement_id]
    this.db.run(sql, values);
  }

  closeConnetion(){
    this.db.close();
  }
}
const connection = new Connection();

module.exports = connection;