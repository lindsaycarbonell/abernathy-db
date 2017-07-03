# abernathy-db
A database of all the community newspapers in the U.S.

** Note to self: make all of these views i/o tables so they don't clutter the db.


## The process for merging with Editor and Publisher data. Let's say we're doing N.C.

### Step 1) Get our state-level data.

`SELECT newspaper_id, newspaper_name, city, county, freq_2004, total_circulation_2004, freq, total_circulation,
CAST(REPLACE(total_circulation, ',', '') AS integer) - CAST(REPLACE(total_circulation_2004, ',', '') AS integer) AS diff
FROM NC_clean
ORDER BY diff DESC`

### Step 2) Get E&P's state-level data.

`SELECT pub_companyName, Streetaddresscity, County, AvgPaidCirc 
FROM ep_2017 
WHERE Streetaddressstate = 'NC'`

### Step 3) Make the first merge attempt

#### Create a table from E&P data for N.C.
  - `CREATE TABLE ep_nc AS SELECT * FROM ep_2017 WHERE Streetaddressstate = 'NC'`
#### Count the number of papers E&P has for N.C.
  - `SELECT * FROM ep_nc`
#### Now count the number of papers we have 
  - `SELECT * FROM NC_clean`

DROP TABLE NC_merge_test

SELECT * FROM AL_clean
DROP TABLE WV_merge_test
CREATE TABLE ep_al AS SELECT * FROM ep_2017 WHERE Streetaddressstate = 'AL'
SELECT * FROM ep_al
/* WV MERGE ON JUST CITY TEST */
CREATE TABLE AL_merge_test AS
SELECT newspaper_id, newspaper_name, AvgPaidCirc, total_circulation, 
ABS(CAST(AvgPaidCirc AS INTEGER) - CAST(REPLACE(total_circulation,',','') AS INTEGER)) AS circDiff,
freq_2004, freq_2017, t1.county,
pub_companyName AS ep_name, t2.County AS ep_county, t1.city AS db_city, t2.Streetaddresscity AS ep_city
FROM AL_clean AS t1
INNER JOIN ep_al AS t2
ON 
/* NAME */
(	t1.newspaper_name = t2.pub_companyName
	OR 
	"The " || trim(replace(t1.newspaper_name,'The','')) = t2.pub_companyName
	OR
	trim(replace(t1.newspaper_name,'The','')) = t2.pub_companyName
/* CITY */
) AND (
	UPPER(t1.city) = UPPER(t2.Streetaddresscity)
)
ORDER BY newspaper_name ASC

CREATE TABLE NC_merge_test_correct AS
SELECT newspaper_id, newspaper_name, AvgPaidCirc, total_circulation, 
ABS(CAST(AvgPaidCirc AS INTEGER) - CAST(REPLACE(total_circulation,',','') AS INTEGER)) AS circDiff,
freq_2004, freq_2017, t1.county,
pub_companyName AS ep_name, t2.County AS ep_county, t1.city AS db_city, t2.Streetaddresscity AS ep_city
FROM NC_clean AS t1
INNER JOIN ep_2017 AS t2
ON 
/* NAME */
(	t1.newspaper_name = t2.pub_companyName
	OR 
	"The " || trim(replace(t1.newspaper_name,'The','')) = t2.pub_companyName
	OR
	trim(replace(t1.newspaper_name,'The','')) = t2.pub_companyName
/* COUNTY */
) AND (
	UPPER(trim(replace(t2.County,'County',''))) = UPPER(t1.county)
/* CITY */
) AND (
	UPPER(t1.city) = UPPER(t2.Streetaddresscity)
)
ORDER BY newspaper_name ASC

SELECT * FROM NC_merge_test /*count all in attempted merge*/


/* EPDB_no_matches */
SELECT newspaper_id, newspaper_name, city, county, freq_2004, total_circulation_2004, freq, total_circulation,
CAST(REPLACE(total_circulation, ',', '') AS integer) - CAST(REPLACE(total_circulation_2004, ',', '') AS integer) AS diff 
FROM AL_clean 
WHERE newspaper_name NOT IN (
SELECT newspaper_name FROM AL_merge_test
)


/* ===== CIRCULATION CHANGES (6 STATES) ===== */

/* 1) get the final merge table */
DROP TABLE NC_merge
CREATE TABLE NC_merge AS
SELECT newspaper_id, newspaper_name, freq_2017, AvgPaidCirc, total_circulation_2017, AvgFreeCirc,
ABS(CAST(AvgPaidCirc AS INTEGER) - CAST(REPLACE(total_circulation,',','') AS INTEGER)) AS circDiff,
freq_2004, total_circulation_2004, t1.city, t1.county
FROM NC_clean AS t1
LEFT OUTER JOIN ep_2017 AS t2
ON 
/* NAME */
(	t1.newspaper_name = t2.pub_companyName
	OR 
	"The " || trim(replace(t1.newspaper_name,'The','')) = t2.pub_companyName
	OR
	trim(replace(t1.newspaper_name,'The','')) = t2.pub_companyName
/* COUNTY */
) AND (
	UPPER(trim(replace(t2.County,'County',''))) = UPPER(t1.county)
/* CITY */
) AND (
	UPPER(t1.city) = UPPER(t2.Streetaddresscity)
)
ORDER BY newspaper_name ASC

SELECT * FROM NC_merge

/* 2) drop the merge test table */
DROP TABLE WV_merge_test

/* 3) put it into the google sheet */
SELECT * FROM WV_merge


/* doing checks */
SELECT t1.newspaper_name, t2.pub_companyName 
FROM AL_clean AS t1
INNER JOIN ep_2017 AS t2 ON
t1.newspaper_name = t2.pub_companyName
OR 
"The " || replace(t1.newspaper_name,'The','') = t2.pub_companyName
OR
replace(t1.newspaper_name,'The','') = t2.pub_companyName
WHERE t2.Streetaddressstate	= 'AL'

SELECT newspaper_name, "The " || trim(replace(newspaper_name,'The','')), trim(replace(newspaper_name,'The',''))
FROM AL_clean WHERE newspaper_name LIKE '%Cullman%'
	
SELECT County, UPPER(trim(replace(County,'County',''))) FROM ep_2017 WHERE Streetaddressstate = 'AL'
AND County LIKE '%Cullman%'
SELECT county, UPPER(county) FROM AL_clean WHERE county LIKE '%Cullman%'

SELECT total_circulation_2017, state FROM all_original WHERE newspaper_id = '15670'
SELECT total_circulation_2017 FROM AL_merge WHERE newspaper_id = '15670'


SELECT * FROM all_original WHERE newspaper_name LIKE '%Star News%'
SELECT * FROM all_original WHERE parent_top_level LIKE '%Womack%'
