# backend/seed.py
import os
import pandas as pd
from database import SessionLocal, engine, base, init_db
import models
import logging 
from datetime import datetime
import numpy as np

logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")

logger=logging.getLogger(__name__)

from sqlalchemy import text

def fix_sequences(db):
    sequences = [
        "SELECT setval('users_user_id_seq', COALESCE((SELECT MAX(user_id) FROM users), 1))",
        "SELECT setval('fields_field_id_seq', COALESCE((SELECT MAX(field_id) FROM fields), 1))",
        "SELECT setval('region_region_id_seq', COALESCE((SELECT MAX(region_id) FROM region), 1))",
        "SELECT setval('satellite_satellite_id_seq', COALESCE((SELECT MAX(satellite_id) FROM satellite), 1))",
        "SELECT setval('crop_cycle_cycle_id_seq', COALESCE((SELECT MAX(cycle_id) FROM crop_cycle), 1))",
        "SELECT setval('weather_weather_id_seq', COALESCE((SELECT MAX(weather_id) FROM weather), 1))",
        "SELECT setval('observation_observation_id_seq', COALESCE((SELECT MAX(observation_id) FROM observation), 1))",
        "SELECT setval('bandvalues_band_id_seq', COALESCE((SELECT MAX(band_id) FROM bandvalues), 1))",
        "SELECT setval('derived_metrics_metric_id_seq', COALESCE((SELECT MAX(metric_id) FROM derived_metrics), 1))",
        "SELECT setval('alert_alert_id_seq', COALESCE((SELECT MAX(alert_id) FROM alert), 1))",
    ]
    for seq in sequences:
        db.execute(text(seq))
    db.commit()
    print(" Sequences fixed!")

class DataBaseSeeder:
    def __init__(self):
        #seed database with initial data from csv files
        self.db=SessionLocal()
        self.records_imported=0

    def seed_from_csv(self):
        #Main Seeding function and inserts data into the database

        try:
            logger.info("="*70)
            logger.info("Starting database seeding process")
            logger.info("="*70)
            
            self.create_tables()#creating tables
            fix_sequences(self.db)

            self.import_regions()
            self.import_users()
            self.import_satellites()
            self.import_field()
            self.import_crop_cycles()
            self.import_observation()
            self.import_band_values()
            self.import_weather()
            self.import_derived_metrics()
            self.import_alerts()

            logger.info("="*70)
            logger.info(f"Database seeding completed successfully. Total records imported: {self.records_imported}")
            logger.info("="*70)
        except Exception as e:
            logger.error(f"Error during database seeding: {e}")
            raise
        finally:
            self.db.close()
    def create_tables(self):

        logger.info("Creating database tables if they do not exist")
        try:
            models.base.metadata.create_all(bind=engine)
            logger.info("Database tables created Successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    def import_regions(self):
        logger.info("Importing regions data ")
        try:
            if not os.path.exists("Data/regions.csv"):
                logger.warning("Regions CSV file not found. Skipping regions import.")
                return
            regions_df=pd.read_csv("Data/regions.csv")
            for _,row in regions_df.iterrows():
                existing_region=self.db.query(models.Region).filter_by(region_id=row["region_id"]).first()
                if existing_region:
                   logger.warning(f"Region with ID {row['region_id']} already exists. Skipping.")
                   continue
                region=models.Region(
                    region_id=row["region_id"],
                    region_name=row["region_name"],
                    climate_type=row["climate_type"],
                    latitude=row.get("latitude"),
                    longitude=row.get("longitude"))
                self.db.add(region)
                self.db.commit()
                logger.info(f"Region {row['region_name']} imported successfully")
                self.records_imported+=1
        except Exception as e:
            logger.error(f"Error importing regions data: {e}")
            self.db.rollback()
            logger.error("Rolled back regions import due to error")
            raise
    def import_users(self):
        logger.info("Importing users data")
        try:
            if not os.path.exists("Data/users.csv"):
                logger.warning("Users CSV file not found. Skipping users import.")
                return
            users_df=pd.read_csv("Data/users.csv")
            for _,row in users_df.iterrows():
                existing_user=self.db.query(models.User).filter_by(user_id=row["user_id"]).first()
                if existing_user:
                    logger.warning(f"User with ID {row['user_id']} already exists. Skipping.")
                    continue
                user=models.User(
                    user_id=row["user_id"],
                    name=row["name"],
                    email=row["email"],
                    role=row["role"],
                    is_active=row.get("is_active",True))
                
                user.set_password(row.get("password","defaultPassword123"))
                self.db.add(user)
                self.db.commit()
                logger.info(f"User {row['name']} imported successfully")
                self.records_imported+=1
        except Exception as e:
            logger.error(f"Error importing users data: {e}")
            self.db.rollback()
            logger.error("Rolled back users import due to error")
            raise
    def import_satellites(self):
        logger.info("Importing satellites data")
        try:
            if not os.path.exists("Data/satellites.csv"):
                logger.warning("Satellites CSV file not found. Skipping satellites import.")
                return
            satellites_df=pd.read_csv("Data/satellites.csv")
            for _,row in satellites_df.iterrows():
                existing_satellite=self.db.query(models.Satellite).filter_by(satellite_id=row["satellite_id"]).first()
                if existing_satellite:
                    logger.warning(f"Satellite with ID {row['satellite_id']} already exists. Skipping.")
                    continue
                satellite=models.Satellite(
                    satellite_id=row["satellite_id"],
                    satellite_name=row.get("name","Unknown"),
                    provider=row.get("provider","Unknown"),
                    resolution=float(str(row.get("resolution",0.0)).replace("m","").replace("km",""))
                )
                self.db.add(satellite)
                self.db.commit()
                logger.info(f"Satellite {row.get('name','Unknown')} imported successfully")
                self.records_imported+=1
        except Exception as e:
            logger.error(f"Error importing satellites data: {e}")
            self.db.rollback()
            logger.error("Rolled back satellites import due to error")
            raise
    def import_field(self):
        logger.info("Importing fields data")
        try:
            if not os.path.exists('Data/fields.csv'):
                logger.warning("Fields.csv not found")
                return
            fields_df=pd.read_csv("Data/fields.csv")
            for _,row in fields_df.iterrows():
                existing_field=self.db.query(models.Field).filter_by(field_id=row["field_id"]).first()
                if existing_field:
                    logger.warning(f"Field with ID {row['field_id']} already exists. Skipping.")
                    continue
                # Check if user exists
                user_exists=self.db.query(models.User).filter_by(user_id=row["user_id"]).first()
                if not user_exists:
                    logger.warning(f"User with ID {row['user_id']} does not exist. Skipping field {row['field_id']}.")
                    continue
                field=models.Field(
                    field_id=row["field_id"],
                    user_id=row["user_id"],
                    region_id=row["region_id"],
                    latitude=row["latitude"],
                    longitude=row["longitude"],
                    area=row["area"],
                    soil_type=row["soil_type"]
                )
                self.db.add(field)
                self.db.commit()
                logger.info(f"Field with ID {row['field_id']} imported successfully")
                self.records_imported+=1
        except Exception as e:
            logger.error(f"Error importing fields data: {e}")
            self.db.rollback()
            logger.error("Rolled back fields import due to error")
            raise
    def import_crop_cycles(self):
        logger.info("Importing crop cycles data")
        try:
            if not os.path.exists("Data/crop_cycles.csv"):
                logger.warning("Crop Cycles CSV file not found. Skipping crop cycles import.")
                return
            crop_cycles_df=pd.read_csv("Data/crop_cycles.csv")
            for _,row in crop_cycles_df.iterrows():
                existing_cycle=self.db.query(models.CropCycle).filter_by(cycle_id=row["cycle_id"]).first()
                if existing_cycle:
                    logger.warning(f"Crop Cycle with ID {row['cycle_id']} already exists. Skipping.")
                    continue
                # Check if field exists
                field_exists=self.db.query(models.Field).filter_by(field_id=row["field_id"]).first()
                if not field_exists:
                    logger.warning(f"Field with ID {row['field_id']} does not exist. Skipping crop cycle {row['cycle_id']}.")
                    continue
                crop_cycle=models.CropCycle(
                    cycle_id=row["cycle_id"],
                    field_id=row["field_id"],
                    crop_name=row["crop_name"],
                    start_date=row["start_date"],
                    expected_harvest_date=row["expected_harvest_date"],
                    
                    
                )
                self.db.add(crop_cycle)
                self.db.commit()
                logger.info(f"Crop Cycle with ID {row['cycle_id']} imported successfully")
                self.records_imported+=1
        except Exception as e:
            logger.error(f"Error importing crop cycles data: {e}")
            self.db.rollback()
            logger.error("Rolled back crop cycles import due to error")
            raise   
    def import_observation(self):
        logger.info("Importing observations data")
        try:
            if not os.path.exists("Data/observations.csv"):
                logger.warning("Observations CSV file not found. Skipping observations import.")
                return
            observations_df=pd.read_csv("Data/observations.csv")
            for _,row in observations_df.iterrows():
                existing_observation=self.db.query(models.Observation).filter_by(observation_id=row["observation_id"]).first()
                if existing_observation:
                    logger.warning(f"Observation with ID {row['observation_id']} already exists. Skipping.")
                    continue
                # Check if field, satellite, and cycle exist
                field_exists=self.db.query(models.Field).filter_by(field_id=row["field_id"]).first()
                satellite_exists=self.db.query(models.Satellite).filter_by(satellite_id=row["satellite_id"]).first()
                cycle_exists=self.db.query(models.CropCycle).filter_by(cycle_id=row["cycle_id"]).first()
                if not field_exists or not satellite_exists or not cycle_exists:
                    logger.warning(f"Missing dependency for observation {row['observation_id']}. Skipping.")
                    continue
                observation=models.Observation(
                    observation_id=row["observation_id"],
                    field_id=row["field_id"],
                    satellite_id=row["satellite_id"],
                    cycle_id=row["cycle_id"],
                    observation_date=row["observation_date"],
                    cloud_cover=row.get("cloud_cover")
                )
                self.db.add(observation)
                self.db.commit()
                logger.info(f"Observation with ID {row['observation_id']} imported successfully")
                self.records_imported+=1
        except Exception as e:
            logger.error(f"Error importing observations data: {e}")
            self.db.rollback()
            logger.error("Rolled back observations import due to error")
            raise
    def import_band_values(self):
        logger.info("Importing band values data")
        try:
            if not os.path.exists("Data/band_values.csv"):
                logger.warning("Band Values CSV file not found. Skipping band values import.")
                return
            band_values_df=pd.read_csv("Data/band_values.csv")
            for _,row in band_values_df.iterrows():
                existing_band_value=self.db.query(models.Bandvalues).filter_by(band_id=row["band_id"]).first()
                if existing_band_value:
                    logger.warning(f"Band Value with ID {row['band_id']} already exists. Skipping.")
                    continue
                # Check if observation exists
                observation_exists=self.db.query(models.Observation).filter_by(observation_id=row["observation_id"]).first()
                if not observation_exists:
                    logger.warning(f"Observation with ID {row['observation_id']} does not exist. Skipping band value {row['band_id']}.")
                    continue
                band_value=models.Bandvalues(
                    band_id=row["band_id"],
                    observation_id=row["observation_id"],
                    band_name=row["band_name"],
                    band_value=row["band_value"]
                )
                self.db.add(band_value)
                self.db.commit()
                logger.info(f"Band Value with ID {row['band_id']} imported successfully")
                self.records_imported+=1
        except Exception as e:
            logger.error(f"Error importing band values data: {e}")
            self.db.rollback()
            logger.error("Rolled back band values import due to error")
            raise   
    def import_weather(self):
        logger.info("Importing weather data")
        try:
            if not os.path.exists("Data/weather.csv"):
                logger.warning("Weather CSV file not found. Skipping weather import.")
                return
            weather_df=pd.read_csv("Data/weather.csv")
            for _,row in weather_df.iterrows():
                existing_weather=self.db.query(models.Weather).filter_by(weather_id=row["weather_id"]).first()
                if existing_weather:
                    logger.warning(f"Weather with ID {row['weather_id']} already exists. Skipping.")
                    continue
                # Check if field exists
                field_exists=self.db.query(models.Field).filter_by(field_id=row["field_id"]).first()
                if not field_exists:
                    logger.warning(f"Field with ID {row['field_id']} does not exist. Skipping weather {row['weather_id']}.")
                    continue
                weather=models.Weather(
                    weather_id=row["weather_id"],
                    field_id=row["field_id"],
                    date=row["date"],
                    temperature=row["temperature"],
                    rainfall=row["rainfall"],
                    humidity=row["humidity"],
                    wind_speed=row.get("wind_speed"),
                    wind_direction=row.get("wind_direction"),
                    pressure=row.get("pressure")
                )
                self.db.add(weather)
                self.db.commit()
                logger.info(f"Weather with ID {row['weather_id']} imported successfully")
                self.records_imported+=1
        except Exception as e:
            logger.error(f"Error importing weather data: {e}")
            self.db.rollback()
            logger.error("Rolled back weather import due to error")
            raise
    def import_derived_metrics(self):
    
        logger.info("\nImporting derived metrics...")
        try:
            if not os.path.exists('Data/derived_metrics.csv'):
                logger.warning("derived_metrics.csv not found, skipping")
                return
            
            df = pd.read_csv('Data/derived_metrics.csv')
            skipped = 0
            
            for _, row in df.iterrows():
                # Convert numpy types to Python native types FIRST
                metric_id = int(row['metric_id'])
                observation_id = int(row['observation_id'])
                
                # CHECK if observation exists first
                obs_exists = self.db.query(models.Observation).filter_by(
                    observation_id=observation_id
                ).first()
                
                if not obs_exists:
                    logger.debug(f"Skipping metric {metric_id}: observation {observation_id} not found")
                    skipped += 1
                    continue
                
                existing = self.db.query(models.DerivedMetrics).filter_by(
                    metric_id=metric_id
                ).first()
                
                if existing:
                    continue
                
                ndvi = float(row['ndvi'])
                evi = float(row['evi'])
                soil_moisture = float(row['soil_moisture'])
                crop_health_score = float(row['crop_health_score'])
                
                metrics = models.DerivedMetrics(
                    metric_id=metric_id,
                    observation_id=observation_id,
                    ndvi=ndvi,
                    evi=evi,
                    soil_moisture=soil_moisture,
                    crop_health_score=crop_health_score
                )
                self.db.add(metrics)
            
                self.db.commit()
                logger.info(f"✓ Imported {len(df) - skipped} derived metrics (skipped {skipped})")
                self.records_imported += 1
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"✗ Failed to import derived metrics: {e}")
            raise
    def import_alerts(self):
        logger.info("Importing alerts data")
        try:
            if not os.path.exists("Data/alerts.csv"):
                logger.warning("Alerts CSV file not found. Skipping alerts import.")
                return
            alerts_df=pd.read_csv("Data/alerts.csv")
            for _,row in alerts_df.iterrows():
                existing_alert=self.db.query(models.Alert).filter_by(alert_id=row["alert_id"]).first()
                if existing_alert:
                    logger.warning(f"Alert with ID {row['alert_id']} already exists. Skipping.")
                    continue
                # Check if field exists
                field_exists=self.db.query(models.Field).filter_by(field_id=int(row["field_id"])).first()
                if not field_exists:
                    logger.warning(f"Field with ID {row['field_id']} does not exist. Skipping alert {row['alert_id']}.")
                    continue
                alert = models.Alert(
                alert_id=int(row['alert_id']),
                field_id=int(row['field_id']),
                observation_id=None,
                alert_type=row['alert_type'],
                severity=row['severity'],
                message=row['message'],
                is_resolved=bool(row['is_resolved']),
                resolved_at=row.get('resolved_at') if pd.notna(row.get('resolved_at')) else None
                )
                self.db.add(alert)
                self.db.commit()
                logger.info(f"Alert with ID {row['alert_id']} imported successfully")
                self.records_imported+=1
        except Exception as e:
            logger.error(f"Error importing alerts data: {e}")
            self.db.rollback()
            logger.error("Rolled back alerts import due to error")
            raise
if __name__=="__main__":
    seeder=DataBaseSeeder()
    seeder.seed_from_csv()
    
    print("Database seeding completed successfully")