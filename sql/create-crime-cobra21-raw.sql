-- create raw zone COBRA 21 table

IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'Crime.cobra21_raw') AND type in (N'U'))
DROP TABLE Crime.cobra21_raw

CREATE TABLE Crime.cobra21_raw (
    id INTEGER NOT NULL IDENTITY(1,1)
    , offense_id varchar(50)
    , rpt_date varchar(50)
    , occur_date varchar(50)
    , occur_day varchar(50)
    , occur_day_num varchar(50)
    , occur_time varchar(50)
    , poss_date varchar(50)
    , poss_time varchar(50)
    , beat varchar(50)
    , zone varchar(50)
    , location varchar(250)
    , ibr_code varchar(50)
    , UC2_Literal varchar(50)
    , neighborhood varchar(50)
    , npu varchar(50)
    , lat varchar(50)
    , long varchar(50)
);