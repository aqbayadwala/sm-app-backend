PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;

INSERT INTO block_listed_tokens VALUES(1,'4eb36cfd-135f-4a2b-9935-419c3caa130b','2025-02-22 13:12:35.301344');
INSERT INTO block_listed_tokens VALUES(2,'c861ad47-9cb0-43ec-a875-3584eb684cfd','2025-02-22 13:31:12.233565');
INSERT INTO block_listed_tokens VALUES(3,'e9abcbd1-e3f7-4adb-b9d8-d395652806fc','2025-02-22 14:17:31.313660');
INSERT INTO block_listed_tokens VALUES(4,'3aeab34c-caeb-43e0-aaa4-2b8814a3f53c','2025-02-24 04:15:05.396512');
INSERT INTO block_listed_tokens VALUES(5,'10e20ed5-02a3-4108-bfa1-84d10eab39de','2025-02-24 04:15:17.986327');
INSERT INTO block_listed_tokens VALUES(6,'aee0d2ad-eda4-4839-b86b-64ab972c18c9','2025-02-24 04:16:41.585061');
INSERT INTO block_listed_tokens VALUES(7,'dbb7df02-c313-43b1-98fd-625744d8bec2','2025-02-24 06:52:26.214554');
INSERT INTO block_listed_tokens VALUES(8,'8ac305a7-3c11-4f70-98f5-3d5da9b2ff4f','2025-02-24 06:53:07.866622');
INSERT INTO block_listed_tokens VALUES(9,'dc287c43-e6f9-427b-95fe-5b39cb3ed5da','2025-02-24 06:55:54.696271');

INSERT INTO moallim VALUES(1,'Mulla Adnan','aqbayadwala@gmail.com','$2b$12$2LqNkQqwbFfnNAi.TZKmF.JVcL9s1nw9snQJlo5wCg1933N69P/16');
INSERT INTO moallim VALUES(6,'A','aqbayadwala6@gmail.com','$2b$12$iov5TbvGLg8QNexDA013cuBMQxAxy8u5lFe6zLUlrkizRYvl5i4va');
INSERT INTO moallim VALUES(7,'Adnan','aqbayadwala9@gmail.com','$2b$12$T621k4zIYDwEwGmMjZ49NeW35aN2CA06iakUo2sxSw/0rGTtt95S.');
INSERT INTO moallim VALUES(8,'a','b@gmail.com','$2b$12$qcVQXQGZ1aA.K2AIV4toxe0JqtRg8U7/ec3C5Nz1.vfVN8bhV.wae');
INSERT INTO moallim VALUES(9,'adnan','c@gmail.com','$2b$12$.Lc3wmx28oCl0A.qAoFc..DhR3phQ1T.kBOeSNKyJebbTvCmgBzaq');
INSERT INTO moallim VALUES(10,'Adnan','e@gmail.com','$2b$12$wRED.KOUKhiwMlpbuMsVZe1KpmoLSplr24CbsmhSEa3yoq5KJPr8W');
INSERT INTO moallim VALUES(11,'Adnan','d@gmail.com','$2b$12$NaRUSkaoAzNu54dYBuMecO8YCMFNW47BzMLuFfVJwxIfK7CAzNhiy');
INSERT INTO moallim VALUES(12,'Adnan Test','aqbayadwala53@gmail.com','$2b$12$UFRtxbgEZEGlW7hoAJnlNehwqYR23PF9EG/LkL6./8ooaliMyDmiy');

INSERT INTO daur VALUES(1,'Sabeah',1);
INSERT INTO daur VALUES(2,'MB',1);
INSERT INTO daur VALUES(3,'Test delete daur',12);

INSERT INTO student VALUES(1,'adnan','A',1);
INSERT INTO student VALUES(2,'ruqaiya','A',1);
INSERT INTO student VALUES(3,'Adnan','A',2);
INSERT INTO student VALUES(4,'Naqiya ezzy','B',1);
INSERT INTO student VALUES(5,'Jamila Badri','D',1);
INSERT INTO student VALUES(6,'Mustafa Saalik','C',1);
INSERT INTO student VALUES(7,'Munira metro','D',1);
INSERT INTO student VALUES(8,'Test one','A',3);
INSERT INTO student VALUES(9,'Test two','B',3);
INSERT INTO student VALUES(10,'Test three','C',3);
INSERT INTO student VALUES(11,'Test four','D',3);
COMMIT;
