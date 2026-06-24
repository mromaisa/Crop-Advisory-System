USE [Crop_Advisory]
GO
/****** Object:  Table [dbo].[Advisory_Logs]    Script Date: 6/25/2026 12:39:47 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Advisory_Logs](
	[advisory_id] [int] IDENTITY(1,1) NOT NULL,
	[farm_id] [int] NOT NULL,
	[crop_id] [int] NOT NULL,
	[soil_id] [int] NOT NULL,
	[generated_date] [date] NULL,
	[match_score] [decimal](18, 0) NULL,
	[rain_score] [decimal](4, 2) NULL,
	[ph_score] [decimal](4, 2) NULL,
	[temp_val] [decimal](4, 2) NULL,
	[weather_id] [int] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[advisory_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[farm_id] ASC,
	[crop_id] ASC,
	[generated_date] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Crop_Season_Junction]    Script Date: 6/25/2026 12:39:47 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Crop_Season_Junction](
	[crop_id] [int] NOT NULL,
	[season_id] [int] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[crop_id] ASC,
	[season_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Crop_Soil_Junction]    Script Date: 6/25/2026 12:39:47 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Crop_Soil_Junction](
	[crop_id] [int] NOT NULL,
	[soil_type_id] [int] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[crop_id] ASC,
	[soil_type_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Crops]    Script Date: 6/25/2026 12:39:47 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Crops](
	[crop_id] [int] NOT NULL,
	[crop_name] [varchar](50) NOT NULL,
	[crop_category] [varchar](20) NULL,
	[min_temp_c] [decimal](5, 2) NOT NULL,
	[max_temp_c] [decimal](5, 2) NOT NULL,
	[min_rainfall_mm] [decimal](8, 2) NOT NULL,
	[max_rainfall_mm] [decimal](8, 2) NOT NULL,
	[min_ph] [decimal](4, 2) NOT NULL,
	[max_ph] [decimal](4, 2) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[crop_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Farm]    Script Date: 6/25/2026 12:39:47 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Farm](
	[farm_id] [int] NOT NULL,
	[farmer_id] [int] NULL,
	[location_id] [int] NULL,
	[farm_name] [varchar](50) NOT NULL,
	[area_acres] [decimal](18, 0) NOT NULL,
	[established_date] [date] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[farm_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Farmer]    Script Date: 6/25/2026 12:39:47 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Farmer](
	[farmer_id] [int] NOT NULL,
	[full_name] [varchar](50) NOT NULL,
	[phone_number] [varchar](20) NOT NULL,
	[email] [varchar](50) NOT NULL,
	[cnic] [varchar](20) NULL,
	[registration_date] [date] NOT NULL,
	[password_hash] [nvarchar](max) NOT NULL,
	[role] [varchar](10) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[farmer_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[cnic] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Location]    Script Date: 6/25/2026 12:39:47 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Location](
	[location_id] [int] NOT NULL,
	[village_name] [varchar](50) NOT NULL,
	[district] [varchar](50) NOT NULL,
	[province] [varchar](50) NOT NULL,
	[latitude] [decimal](18, 0) NOT NULL,
	[longitude] [decimal](18, 0) NOT NULL,
	[altitude] [int] NULL,
PRIMARY KEY CLUSTERED 
(
	[location_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Season]    Script Date: 6/25/2026 12:39:47 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Season](
	[season_id] [int] NOT NULL,
	[season_type] [varchar](20) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[season_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[season_type] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
 CONSTRAINT [uq_season_type] UNIQUE NONCLUSTERED 
(
	[season_type] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Soil_Profile]    Script Date: 6/25/2026 12:39:47 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Soil_Profile](
	[soil_id] [int] NOT NULL,
	[farm_id] [int] NULL,
	[ph_level] [decimal](4, 2) NOT NULL,
	[organic_matter_pct] [decimal](18, 0) NULL,
	[sample_date] [date] NOT NULL,
	[soil_type_id] [int] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[soil_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Soil_Type]    Script Date: 6/25/2026 12:39:47 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Soil_Type](
	[soil_type_id] [int] NOT NULL,
	[soil_type] [varchar](20) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[soil_type_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[soil_type] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
 CONSTRAINT [uq_soil_type] UNIQUE NONCLUSTERED 
(
	[soil_type] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Weather_Record]    Script Date: 6/25/2026 12:39:47 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Weather_Record](
	[weather_id] [int] NOT NULL,
	[location_id] [int] NULL,
	[record_date] [date] NOT NULL,
	[average_temp_c] [decimal](5, 2) NOT NULL,
	[min_temp_c] [decimal](18, 0) NULL,
	[max_temp_c] [decimal](18, 0) NULL,
	[rainfall_mm] [decimal](8, 2) NOT NULL,
	[humidity_pct] [decimal](18, 0) NULL,
	[season_id] [int] NULL,
PRIMARY KEY CLUSTERED 
(
	[weather_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[Crops] ADD  CONSTRAINT [inc_crops]  DEFAULT (NEXT VALUE FOR [dbo].[increment_crop]) FOR [crop_id]
GO
ALTER TABLE [dbo].[Farm] ADD  CONSTRAINT [inc_farm]  DEFAULT (NEXT VALUE FOR [dbo].[increment_farm]) FOR [farm_id]
GO
ALTER TABLE [dbo].[Farmer] ADD  CONSTRAINT [inc_farmer]  DEFAULT (NEXT VALUE FOR [dbo].[increment_farmer]) FOR [farmer_id]
GO
ALTER TABLE [dbo].[Location] ADD  CONSTRAINT [inc_location]  DEFAULT (NEXT VALUE FOR [dbo].[increment_location]) FOR [location_id]
GO
ALTER TABLE [dbo].[Season] ADD  CONSTRAINT [inc_season]  DEFAULT (NEXT VALUE FOR [dbo].[increment]) FOR [season_id]
GO
ALTER TABLE [dbo].[Soil_Profile] ADD  CONSTRAINT [inc_soil]  DEFAULT (NEXT VALUE FOR [dbo].[increment_soil]) FOR [soil_id]
GO
ALTER TABLE [dbo].[Soil_Type] ADD  CONSTRAINT [inc_soil_type]  DEFAULT (NEXT VALUE FOR [dbo].[increment_soil_type]) FOR [soil_type_id]
GO
ALTER TABLE [dbo].[Weather_Record] ADD  CONSTRAINT [inc_weather_record]  DEFAULT (NEXT VALUE FOR [dbo].[increment]) FOR [weather_id]
GO
ALTER TABLE [dbo].[Advisory_Logs]  WITH CHECK ADD FOREIGN KEY([crop_id])
REFERENCES [dbo].[Crops] ([crop_id])
GO
ALTER TABLE [dbo].[Advisory_Logs]  WITH CHECK ADD FOREIGN KEY([farm_id])
REFERENCES [dbo].[Farm] ([farm_id])
GO
ALTER TABLE [dbo].[Advisory_Logs]  WITH CHECK ADD FOREIGN KEY([soil_id])
REFERENCES [dbo].[Soil_Profile] ([soil_id])
GO
ALTER TABLE [dbo].[Advisory_Logs]  WITH CHECK ADD  CONSTRAINT [fk_weather_on_advisory] FOREIGN KEY([weather_id])
REFERENCES [dbo].[Weather_Record] ([weather_id])
GO
ALTER TABLE [dbo].[Advisory_Logs] CHECK CONSTRAINT [fk_weather_on_advisory]
GO
ALTER TABLE [dbo].[Crop_Season_Junction]  WITH CHECK ADD FOREIGN KEY([crop_id])
REFERENCES [dbo].[Crops] ([crop_id])
GO
ALTER TABLE [dbo].[Crop_Season_Junction]  WITH CHECK ADD FOREIGN KEY([season_id])
REFERENCES [dbo].[Season] ([season_id])
GO
ALTER TABLE [dbo].[Crop_Soil_Junction]  WITH CHECK ADD FOREIGN KEY([crop_id])
REFERENCES [dbo].[Crops] ([crop_id])
GO
ALTER TABLE [dbo].[Crop_Soil_Junction]  WITH CHECK ADD FOREIGN KEY([soil_type_id])
REFERENCES [dbo].[Soil_Type] ([soil_type_id])
GO
ALTER TABLE [dbo].[Farm]  WITH CHECK ADD FOREIGN KEY([farmer_id])
REFERENCES [dbo].[Farmer] ([farmer_id])
GO
ALTER TABLE [dbo].[Farm]  WITH CHECK ADD FOREIGN KEY([location_id])
REFERENCES [dbo].[Location] ([location_id])
GO
ALTER TABLE [dbo].[Soil_Profile]  WITH CHECK ADD FOREIGN KEY([farm_id])
REFERENCES [dbo].[Farm] ([farm_id])
GO
ALTER TABLE [dbo].[Soil_Profile]  WITH CHECK ADD  CONSTRAINT [fk_soil_type] FOREIGN KEY([soil_type_id])
REFERENCES [dbo].[Soil_Type] ([soil_type_id])
GO
ALTER TABLE [dbo].[Soil_Profile] CHECK CONSTRAINT [fk_soil_type]
GO
ALTER TABLE [dbo].[Weather_Record]  WITH CHECK ADD FOREIGN KEY([location_id])
REFERENCES [dbo].[Location] ([location_id])
GO
ALTER TABLE [dbo].[Weather_Record]  WITH CHECK ADD  CONSTRAINT [fk_season] FOREIGN KEY([season_id])
REFERENCES [dbo].[Season] ([season_id])
GO
ALTER TABLE [dbo].[Weather_Record] CHECK CONSTRAINT [fk_season]
GO
ALTER TABLE [dbo].[Crops]  WITH CHECK ADD  CONSTRAINT [chk_crop_name_len] CHECK  ((len(Trim([crop_name]))>(0)))
GO
ALTER TABLE [dbo].[Crops] CHECK CONSTRAINT [chk_crop_name_len]
GO
ALTER TABLE [dbo].[Crops]  WITH CHECK ADD  CONSTRAINT [chk_crop_ph_range] CHECK  (([min_ph]<[max_ph]))
GO
ALTER TABLE [dbo].[Crops] CHECK CONSTRAINT [chk_crop_ph_range]
GO
ALTER TABLE [dbo].[Crops]  WITH CHECK ADD  CONSTRAINT [chk_crop_ph_vals] CHECK  (([min_ph]>=(0) AND [min_ph]<=(14) AND ([max_ph]>=(0) AND [max_ph]<=(14))))
GO
ALTER TABLE [dbo].[Crops] CHECK CONSTRAINT [chk_crop_ph_vals]
GO
ALTER TABLE [dbo].[Crops]  WITH CHECK ADD  CONSTRAINT [chk_crop_rain_range] CHECK  (([min_rainfall_mm]<[max_rainfall_mm]))
GO
ALTER TABLE [dbo].[Crops] CHECK CONSTRAINT [chk_crop_rain_range]
GO
ALTER TABLE [dbo].[Crops]  WITH CHECK ADD  CONSTRAINT [chk_crop_rain_vals] CHECK  (([min_rainfall_mm]>=(0) AND [max_rainfall_mm]<=(5000)))
GO
ALTER TABLE [dbo].[Crops] CHECK CONSTRAINT [chk_crop_rain_vals]
GO
ALTER TABLE [dbo].[Crops]  WITH CHECK ADD  CONSTRAINT [chk_crop_temp_range] CHECK  (([min_temp_c]<[max_temp_c]))
GO
ALTER TABLE [dbo].[Crops] CHECK CONSTRAINT [chk_crop_temp_range]
GO
ALTER TABLE [dbo].[Crops]  WITH CHECK ADD  CONSTRAINT [chk_crop_temp_vals] CHECK  (([min_temp_c]>=(-20) AND [min_temp_c]<=(60) AND ([max_temp_c]>=(-20) AND [max_temp_c]<=(60))))
GO
ALTER TABLE [dbo].[Crops] CHECK CONSTRAINT [chk_crop_temp_vals]
GO
ALTER TABLE [dbo].[Farm]  WITH CHECK ADD  CONSTRAINT [chk_farm_area] CHECK  (([area_acres]>(0) AND [area_acres]<=(100000)))
GO
ALTER TABLE [dbo].[Farm] CHECK CONSTRAINT [chk_farm_area]
GO
ALTER TABLE [dbo].[Farm]  WITH CHECK ADD  CONSTRAINT [chk_farm_estdate] CHECK  (([established_date]<=CONVERT([date],getdate())))
GO
ALTER TABLE [dbo].[Farm] CHECK CONSTRAINT [chk_farm_estdate]
GO
ALTER TABLE [dbo].[Farm]  WITH CHECK ADD  CONSTRAINT [chk_farm_name_len] CHECK  ((len(Trim([farm_name]))>(0)))
GO
ALTER TABLE [dbo].[Farm] CHECK CONSTRAINT [chk_farm_name_len]
GO
ALTER TABLE [dbo].[Farmer]  WITH CHECK ADD  CONSTRAINT [chk_farmer_cnic] CHECK  (([cnic] like '[0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9]'))
GO
ALTER TABLE [dbo].[Farmer] CHECK CONSTRAINT [chk_farmer_cnic]
GO
ALTER TABLE [dbo].[Farmer]  WITH CHECK ADD  CONSTRAINT [chk_farmer_name_len] CHECK  ((len(Trim([full_name]))>(0)))
GO
ALTER TABLE [dbo].[Farmer] CHECK CONSTRAINT [chk_farmer_name_len]
GO
ALTER TABLE [dbo].[Farmer]  WITH CHECK ADD  CONSTRAINT [chk_farmer_phone] CHECK  ((len([phone_number])>=(10)))
GO
ALTER TABLE [dbo].[Farmer] CHECK CONSTRAINT [chk_farmer_phone]
GO
ALTER TABLE [dbo].[Farmer]  WITH CHECK ADD  CONSTRAINT [chk_farmer_regdate] CHECK  (([registration_date]<=CONVERT([date],getdate())))
GO
ALTER TABLE [dbo].[Farmer] CHECK CONSTRAINT [chk_farmer_regdate]
GO
ALTER TABLE [dbo].[Farmer]  WITH CHECK ADD  CONSTRAINT [chk_role] CHECK  (([role]='admin' OR [role]='farmer'))
GO
ALTER TABLE [dbo].[Farmer] CHECK CONSTRAINT [chk_role]
GO
ALTER TABLE [dbo].[Location]  WITH CHECK ADD  CONSTRAINT [chk_loc_alt] CHECK  (([altitude]>=(-500) AND [altitude]<=(9000)))
GO
ALTER TABLE [dbo].[Location] CHECK CONSTRAINT [chk_loc_alt]
GO
ALTER TABLE [dbo].[Location]  WITH CHECK ADD  CONSTRAINT [chk_loc_lat] CHECK  (([latitude]>=(-90) AND [latitude]<=(90)))
GO
ALTER TABLE [dbo].[Location] CHECK CONSTRAINT [chk_loc_lat]
GO
ALTER TABLE [dbo].[Location]  WITH CHECK ADD  CONSTRAINT [chk_loc_lng] CHECK  (([longitude]>=(-180) AND [longitude]<=(180)))
GO
ALTER TABLE [dbo].[Location] CHECK CONSTRAINT [chk_loc_lng]
GO
ALTER TABLE [dbo].[Season]  WITH CHECK ADD  CONSTRAINT [chk_season_type] CHECK  (([season_type]='Perennial' OR [season_type]='Spring-Zaid' OR [season_type]='Late Kharif' OR [season_type]='Early Kharif' OR [season_type]='Late Rabi' OR [season_type]='Early Rabi' OR [season_type]='Monsoon' OR [season_type]='Rabi' OR [season_type]='Kharif' OR [season_type]='Zaid'))
GO
ALTER TABLE [dbo].[Season] CHECK CONSTRAINT [chk_season_type]
GO
ALTER TABLE [dbo].[Soil_Profile]  WITH CHECK ADD  CONSTRAINT [chk_sp_organic] CHECK  (([organic_matter_pct]>=(0) AND [organic_matter_pct]<=(100)))
GO
ALTER TABLE [dbo].[Soil_Profile] CHECK CONSTRAINT [chk_sp_organic]
GO
ALTER TABLE [dbo].[Soil_Profile]  WITH CHECK ADD  CONSTRAINT [chk_sp_ph] CHECK  (([ph_level]>=(0) AND [ph_level]<=(14)))
GO
ALTER TABLE [dbo].[Soil_Profile] CHECK CONSTRAINT [chk_sp_ph]
GO
ALTER TABLE [dbo].[Soil_Profile]  WITH CHECK ADD  CONSTRAINT [chk_sp_sampledate] CHECK  (([sample_date]<=CONVERT([date],getdate())))
GO
ALTER TABLE [dbo].[Soil_Profile] CHECK CONSTRAINT [chk_sp_sampledate]
GO
ALTER TABLE [dbo].[Weather_Record]  WITH CHECK ADD  CONSTRAINT [chk_wr_avg_temp] CHECK  (([average_temp_c]>=(-20) AND [average_temp_c]<=(60)))
GO
ALTER TABLE [dbo].[Weather_Record] CHECK CONSTRAINT [chk_wr_avg_temp]
GO
ALTER TABLE [dbo].[Weather_Record]  WITH CHECK ADD  CONSTRAINT [chk_wr_humidity] CHECK  (([humidity_pct]>=(0) AND [humidity_pct]<=(100)))
GO
ALTER TABLE [dbo].[Weather_Record] CHECK CONSTRAINT [chk_wr_humidity]
GO
ALTER TABLE [dbo].[Weather_Record]  WITH CHECK ADD  CONSTRAINT [chk_wr_max_temp] CHECK  (([max_temp_c]>=(-20) AND [max_temp_c]<=(60)))
GO
ALTER TABLE [dbo].[Weather_Record] CHECK CONSTRAINT [chk_wr_max_temp]
GO
ALTER TABLE [dbo].[Weather_Record]  WITH CHECK ADD  CONSTRAINT [chk_wr_min_temp] CHECK  (([min_temp_c]>=(-20) AND [min_temp_c]<=(60)))
GO
ALTER TABLE [dbo].[Weather_Record] CHECK CONSTRAINT [chk_wr_min_temp]
GO
ALTER TABLE [dbo].[Weather_Record]  WITH CHECK ADD  CONSTRAINT [chk_wr_rainfall] CHECK  (([rainfall_mm]>=(0) AND [rainfall_mm]<=(2000)))
GO
ALTER TABLE [dbo].[Weather_Record] CHECK CONSTRAINT [chk_wr_rainfall]
GO
ALTER TABLE [dbo].[Weather_Record]  WITH CHECK ADD  CONSTRAINT [chk_wr_temp_order] CHECK  (([min_temp_c]<=[average_temp_c] AND [average_temp_c]<=[max_temp_c]))
GO
ALTER TABLE [dbo].[Weather_Record] CHECK CONSTRAINT [chk_wr_temp_order]
GO
