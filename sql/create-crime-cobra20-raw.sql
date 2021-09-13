
IF OBJECT_ID('Crime.cobra20_raw') IS NOT NULL DROP TABLE Crime.cobra20_raw;
GO

create table Crime.cobra20_raw (
    id INT NOT NULL IDENTITY(1,1)
        PRIMARY KEY WITH (DATA_COMPRESSION=PAGE)
    , offense_id varchar(50)
    , rpt_date varchar(50)
    , occur_date varchar(50)
    , occur_time varchar(50)
    , poss_date varchar(50)
    , poss_time varchar(50)
    , beat varchar(50)
    , apt_office_prefix varchar(50)
    , apt_office_num varchar(50)
    , location varchar(250)
    , watch varchar(50)
    , MinOfucr varchar(50)
    , dispo_code varchar(50)
    , Shift varchar(50)
    , location_type varchar(50)
    , UC2_Literal varchar(50)
    , ibr_code varchar(50)
    , UCR_Number varchar(50)
    , neighborhood varchar(50)
    , npu varchar(50)
    , lat varchar(50)
    , long varchar(50)
    , inserted_on datetime not null default SYSDATETIME()
);