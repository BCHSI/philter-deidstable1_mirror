phi_categories = ['Age', 'Contact', 'Date', 'ID', 'Location', 'Name', 'Other']

ucsf_category_dict = {'Date':'Date',
                      'Provider_Name':'Name',
                      'Phone_Fax':'Contact',
                      'Age':'Age',
                      'Patient_Name_or_Family_Member_Name':'Name',
                      'Patient_Address':'Location',
                      'Patient_Initials':'Name',
                      'Provider_Address_or_Location':'Location',
                      'Provider_Initials':'Name',
                      'Provider_Certificate_or_License':'ID',
                      'Patient_Medical_Record_Id':'ID',
                      'Patient_Account_Number':'ID',
                      'Patient_Social_Security_Number':'ID',
                      'Patient_Vehicle_or_Device_Id':'ID',
                      'Patient_Unique_Id':'ID',
                      'Diagnosis_Code_ICD_or_International':'ID',
                      'Procedure_or_Billing_Code':'ID',
                      'Medical_Department_Name':'Location',
                      'Email':'Contact',
                      'URL_IP':'Contact',
                      'Patient_Biometric_Id_or_Face_Photo':'ID',
                      'Patient_Language_Spoken':'Other',
                      'Patient_Place_Of_Work_or_Occupation':'Location',
                      'Patient_Certificate_or_License':'ID',
                      'Medical_Research_Study_Name_or_Number':'ID',
                      'Teaching_Institution_Name':'Location',
                      'Non_UCSF_Medical_Institution_Name':'Location',
                      'Medical_Institution_Abbreviation':'Location',
                      'TOWN':'Location',
                      'Unclear':'Other'
}
ucsf_tags = list(ucsf_category_dict.keys())
ucsf_include_tags = ['Date', 'Provider_Name', 'Phone_Fax',
                     'Patient_Name_or_Family_Member_Name', 'Patient_Address',
                     'Provider_Address_or_Location',
                     'Provider_Certificate_or_License',
                     'Patient_Medical_Record_Id', 'Patient_Account_Number',
                     'Patient_Social_Security_Number',
                     'Patient_Vehicle_or_Device_Id', 'Patient_Unique_Id',
                     'Procedure_or_Billing_Code', 'Email', 'URL_IP',
                     'Patient_Biometric_Id_or_Face_Photo',
                     'Patient_Certificate_or_License', 'Age',
                     'Patient_Initials', 'Provider_Initials', 'TOWN']
ucsf_patient_tags = ['Date', 'Phone_Fax', 'Age',
                     'Patient_Name_or_Family_Member_Name', 'Patient_Address',
                     'Patient_Initials', 'Patient_Medical_Record_Id',
                     'Patient_Account_Number',
                     'Patient_Social_Security_Number',
                     'Patient_Vehicle_or_Device_Id', 'Patient_Unique_Id',
                     'Email', 'URL_IP', 'Patient_Biometric_Id_or_Face_Photo',
                     'Patient_Certificate_or_License']
ucsf_provider_tags = ['Provider_Name', 'Phone_Fax',
                      'Provider_Address_or_Location', 'Provider_Initials',
                      'Provider_Certificate_or_License', 'Email', 'URL_IP']
            
i2b2_category_dict = {'DOCTOR':'Name',
                      'PATIENT':'Name',
                      'DATE':'Date',
                      'MEDICALRECORD':'ID',
                      'IDNUM':'ID',
                      'DEVICE':'ID',
                      'USERNAME':'Contact',
                      'PHONE':'Contact',
                      'EMAIL':'Contact',
                      'FAX':'Contact',
                      'CITY':'Location',
                      'STATE':'Location',
                      'ZIP':'Location',
                      'STREET':'Location',
                      'LOCATION-OTHER':'Location',
                      'HOSPITAL':'Location',
                      'AGE':'Age'
}
i2b2_tags = list(i2b2_category_dict.keys())
i2b2_include_tags = ['DOCTOR', 'PATIENT', 'DATE', 'MEDICALRECORD', 'IDNUM',
                     'DEVICE', 'USERNAME', 'PHONE', 'EMAIL', 'FAX', 'CITY',
                     'STATE', 'ZIP', 'STREET', 'LOCATION-OTHER', 'HOSPITAL',
                     'AGE']
i2b2_patient_tags = ['PATIENT', 'DATE', 'MEDICALRECORD', 'IDNUM', 'DEVICE',
                     'USERNAME', 'PHONE', 'EMAIL', 'FAX', 'CITY', 'STATE',
                     'ZIP', 'STREET', 'LOCATION-OTHER', 'HOSPITAL', 'AGE']
i2b2_provider_tags = ['DOCTOR', 'DATE', 'USERNAME', 'PHONE', 'EMAIL', 'FAX',
                      'CITY', 'STATE', 'ZIP', 'STREET', "LOCATION-OTHER",
                      'HOSPITAL']
town_city_exclude_tags = ['friend', 'cousin', 'brother', 'normal', 'nephew', 'likely', 'unknown', 'rescue' ,'decline']


large_town_exclude_tags = ['abilene','addison','adelanto','aiken','akron','alabaster','alameda','alamogordo','albany','albuquerque','alexandria','algonquin','alhambra','aliso','allen','allis','alpharetta','altamonte','alto','altoona','altos','amarillo','amboy','american','ames','ana','anaheim','anchorage','and','anderson','andover','angeles','angelo','ankeny','ann','annapolis','antioch','antonio','apache','apex','apopka','apple','appleton','arbor','arcadia','arlington','arrow','arthur','arvada','asheville','atascadero','athens clarke','atlanta','atlantic','attleboro','auburn','augusta richmond','aurora','austin','aventura','avondale','azusa','bakersfield','balance','baldwin','ballwin','baltimore','bangor','banning','banos','bar','barbara','barnstable','bartlesville','bartlett','baton','battle','bay','bayonne','beach','beaumont','beavercreek','beaverton','bedford','bell','belleville','bellevue','bellflower','bellingham','beloit','bend','benton','bentonville','berkeley','berlin','bern','bernardino','berwyn','bethel','bethlehem','bettendorf','beverly','billings','biloxi','binghamton','birmingham','bismarck','blacksburg','blaine','bloomington','blue','bluff','bluffs','boca','boise','bolingbrook','bonita','borough','bossier','boston','bothell','boulder','bountiful','bow','bowie','bowling','boynton','bozeman','bradenton','braintree','branch','braunfels','brea','bremerton','brentwood','bridgeport','brighton','bristol','britain','brockton','broken','brookfield','brookhaven','brooklyn','broomfield','brownsville','bruno','brunswick','bryan','buckeye','buena','buenaventura','buffalo','bullhead','burbank','burien','burleson','burlingame','burlington','burnsville','butte silver','cajon','caldwell','calexico','calumet','camarillo','cambridge','camden','campbell','canton','cape','capistrano','carlos','carlsbad','carmel','carol','carpentersville','carrollton','carson','cary','casa','casper','castle','cathedral','cdp','cedar','centennial','center','centro','ceres','cerritos','champaign','chandler','chapel','charles','charleston','charlotte','charlottesville','chattanooga','chelsea','chesapeake','chester','chesterfield','cheyenne','chicago','chico','chicopee','chino','christi','chula','cibolo','cicero','cincinnati','citrus','clair','claire','clara','claremont','clarita','clarksville','clearfield','clearwater','cleburne','clemente','clermont','cleveland','clifton','cloud','clovis','coachella','coast','coconut','coeur','college','collierville','collins','colony','colorado','colton','columbia','columbus','commerce','compton','concord','conroe','consolidated','conway','cookeville','coon','cooper','coppell','copperas','coral','cordova','corners','corona','corpus','corvallis','costa','cottage','cottonwood','council','county','cove','covina','covington','cranston','creek','crosse','crown','cruces','cruz','crystal','cucamonga','culver','cupertino','cutler','cuyahoga','cypress','d alene','dallas','dalton','daly','dana','danbury','dania','danville','davenport','davie','davis','dayton','daytona','de','dearborn','decatur','deer','deerfield','dekalb','del','deland','delano','delaware','delray','deltona','denton','denver','des','desert','desoto','detroit','diamond','diego','dimas','doral','dothan','douglasville','dover','downers','downey','draper','du','dublin','dubuque','duluth','duncanville','dunedin','dunwoody','durham','eagan','eagle','east','eastpointe','eastvale','eau','eden','edina','edinburg','edmond','edmonds','el','elgin','elizabeth','elk','elkhart','elm','elmhurst','elsinore','elyria','encinitas','englewood','enid','erie','escondido','estates','estero','euclid','eugene','euless','evanston','evansville','everett','fair','fairbanks','fairborn','fairfield','fall','falls','fargo','farmers','farmington','fayetteville','fe','federal','findlay','fishers','fitchburg','flagstaff','flint','florence','florissant','flower','folsom','fond','fontana','forest','fork','forks','fort','foster','fountain','framingham','francisco','franklin','frederick','freeport','fremont','fresno','friendswood','frisco','fullerton','fulton','gables','gabriel','gadsden','gahanna','gainesville','gaithersburg','galesburg','gallatin','galveston','garden','gardena','gardens','garfield','garland','garner','gary','gastonia','gate','gatos','george','gilbert','gillette','gilroy','girardeau','glendale','glendora','glenview','gloucester','goldsboro','goleta','goodyear','goose','goshen','government','grand','grande','grants','grapevine','great','greeley','green','greenacres','greenfield','greensboro','greenville','greenwood','greer','gresham','grove','gulfport','gurnee','habra','hackensack','hallandale','haltom','hamilton','hammond','hampton','hanford','hanover','harker','harlingen','harrisburg','harrisonburg','hartford','hattiesburg','haute','havasu','haven','haverhill','hawthorne','hayward','head','heights','helena','hemet','hempstead','henderson','hendersonville','herriman','hesperia','hialeah','hickory','high','highland','hill','hilliard','hills','hillsboro','hilton','hinesville','hobbs','hoboken','hoffman','holladay','holland','hollister','holly','hollywood','holyoke','homestead','honolulu','hoover','hopkinsville','hot','houma','houston','huber','huntersville','huntington','huntsville','hurst','hutchinson','idaho','independence','indian','indianapolis','indio','inglewood','inver','iowa','irvine','irving','island','issaquah','ithaca','jacinto','jackson','jacksonville','janesville','jefferson','jeffersonville','jersey','johns','johnson','joliet','jonesboro','joplin','jordan','jose','joseph','juan','juliet','junction','juneau','jupiter','jurupa','kalamazoo','kannapolis','kansas','kaysville','kearney','kearns','kearny','keizer','keller','kenner','kennesaw','kennewick','kenosha','kent','kentwood','kettering','killeen','kingman','kingsport','kirkland','kissimmee','knoxville','kokomo','kyle','la','lac','lacey','lafayette','lagrange','laguna','lake','lakeland','lakes','lakeville','lakewood','lancaster','land','lansing','laramie','laredo','largo','las','lauderdale','lauderhill','lawn','lawndale','lawrence','lawton','layton','league','leander','leandro','leavenworth','leawood','lebanon','lee','lee s','leesburg','lehi','lenexa','leominster','lewiston','lewisville','lexington fayette','liberty','lima','lincoln','linda','linden','little','littleton','livermore','livonia','lodi','logan','lombard','lompoc','long','longmont','longview','lorain','los','louis','louisvillejefferson','loveland','lowell','lubbock','lucie','lufkin','luis','lynchburg','lynn','lynnwood','lynwood','macon bibb','madera','madison','malden','manassas','manchester','manhattan','manitowoc','mankato','mansfield','manteca','maple','maplewood','marana','marcos','margarita','margate','maria','maricopa','marietta','marion','marlborough','martinez','marysville','mason','massillon','mateo','matthews','mcallen','mckinney','mcminnville','medford','melbourne','memphis','menifee','menlo','menomonee','mentor','merced','meriden','meridian','merrillville','mesa','mesquite','methuen','metro','metropolitan','miami','michigan','midland','midlothian','midvale','midwest','milford','millcreek','milpitas','milton','milwaukee','minneapolis','minnetonka','minot','mirada','mirage','miramar','mishawaka','mission','missoula','missouri','mobile','modesto','moines','moline','monica','monroe','monrovia','montclair','monte','montebello','monterey','montgomery','moore','mooresville','moorhead','moorpark','moreno','morgan','mound','mount','mountain','muncie','mundelein','municipality','murfreesboro','murray','murrieta','muskegon','muskogee','myers','myrtle','nacogdoches','nampa','napa','naperville','nashua','nashville davidson','national','naugatuck','new','newark','newnan','newport','news','newton','niagara','nicholasville','niguel','noblesville','norfolk','normal','norman','north','northbrook','northglenn','norwalk','norwich','novato','novi','oak','oakland','oakley','oaks','obispo','ocala','oceanside','ocoee','odessa','o fallon','ogden','oklahoma','olathe','olive','olmsted','olympia','omaha','ontario','opelika','orange','oregon','orem','orland','orlando','orleans','ormond','oro','oshkosh','oswego','overland','oviedo','owasso','owensboro','oxnard','pablo','pacifica','palatine','palm','palmdale','palo','palos','panama','paramount','park','parker','parkland','parma','pasadena','pasco','paso','paso','pass','passaic','paterson','paul','pawtucket','peabody','peachtree','pearland','pekin','pembroke','pensacola','peoria','perris','perth','petaluma','peters','petersburg','pflugerville','pharr','phenix','philadelphia','phoenix','pico','pierce','pine','pinellas','pines','pittsburg','pittsburgh','pittsfield','place','placentia','plaines','plainfield','plains','plano','plant','plantation','pleasant','pleasanton','plymouth','pocatello','point','pomona','pompano','pontiac','port','portage','porte','porterville','portland','portsmouth','post','poughkeepsie','poway','prairie','prattville','prescott','princeton','prospect','providence','provo','pueblo','puente','pullman','puyallup','queen','quincy','quinta','racine','rafael','raleigh','ramon','rancho','randolph','rapid','rapids','raton','reading','redding','redlands','redmond','redondo','redwood','reno','renton','revere','reynoldsburg','rialto','richardson','richfield','richland','richmond','ridge','ridgeville','rio','river','rivera','riverside','riverton','riviera','roanoke','robins','robles','robles','rochelle','rochester','rock','rockford','rocklin','rockville','rockwall','rocky','rogers','rohnert','rome','romeoville','rosa','rosemead','rosenberg','roseville','roswell','rouge','round','rowlett','roy','royal','royalton','sacramento','saginaw','sahuarita','salem','salina','salinas','salisbury','salt','sammamish','san','sandy','sanford','santa','santee','sarasota','saratoga','savage','savannah','sayreville','schaumburg','schenectady','schertz','scottsdale','scranton','seaside','seattle','shakopee','shawnee','sheboygan','shelton','sherman','sherwood','shoreline','shores','shreveport','sierra','simi','sioux','skokie','smith','smyrna','socorro','somerville','south','southaven','southfield','southlake','spanish','sparks','spartanburg','spokane','spring','springdale','springfield','springs','springville','st.','stamford','stanton','state','statesboro','station','sterling','stevens','stillwater','stockton','stonecrest','stow','stream','streamwood','strongsville','suffolk','sugar','summerville','summit','sumter','sun','sunnyvale','sunrise','surprise','syracuse','tacoma','tallahassee','tamarac','tampa','taunton','taylor','taylorsville','temecula','tempe','temple','terre','texarkana','texas','the','thornton','thousand','tigard','tinley','titusville','toledo','tonawanda','tooele','topeka','torrance','torrington','tracy','trail','trenton','troy','tucker','tucson','tulare','tulsa','tupelo','turlock','tuscaloosa','tustin','twin','tyler','unified','union','university','upland','upper','urban','urbana','urbandale','utica','vacaville','valdosta','vallejo','valley','valparaiso','vancouver','vegas','ventura','verdes','vergne','verne','vernon','vestavia','victoria','victorville','viejo','view','village','vineland','virginia','visalia','vista','waco','wake','walla','walnut','waltham','warner','warren','warwick','washington','waterbury','waterloo','watsonville','waukegan','waukesha','wausau','wauwatosa','waxahachie','way','wayne','weatherford','wellington','wenatchee','wentzville','weslaco','west','westerville','westfield','westlake','westland','westminster','weston','weymouth','wheat','wheaton','wheeling','white','whittier','wichita','wildomar','wildwood','wilkes barre','wilmington','wilson','winston salem','winter','woburn','woodbury','woodland','woodridge','woodstock','woonsocket','worcester','worth','wylie','wyoming','yakima','yonkers','yorba','york','yuba','yucaipa','yuma']
