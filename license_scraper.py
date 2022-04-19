from medical_license_function import select_licenses_by_county, cat_outputs
import sys

# Handle command line args
counties = ['Arkansas',
            'Ashley',
            'Baxter',
            'Benton',
            'Boone',
            'Bradley',
            'Calhoun',
            'Carroll',
            'Chicot',
            'Clark',
            'Clay',
            'Cleburne',
            'Cleveland',
            'Columbia',
            'Conway',
            'Craighead',
            'Crawford',
            'Crittenden',
            'Cross',
            'Dallas',
            'Desha',
            'Drew',
            'Faulkner',
            'Franklin',
            'Fulton',
            'Garland',
            'Grant',
            'Greene',
            'Hempstead',
            'Hot Spring',
            'Howard',
            'Independence',
            'Izard',
            'Jackson',
            'Jefferson',
            'Johnson',
            'Lafayette',
            'Lawrence',
            'Lee',
            'Lincoln',
            'Little River',
            'Logan',
            'Lonoke',
            'Madison',
            'Marion',
            'Miller',
            'Mississippi',
            'Monroe',
            'Montgomery',
            'Nevada',
            'Newton',
            'Ouachita',
            'Perry',
            'Phillips',
            'Pike',
            'Poinsett',
            'Polk',
            'Pope',
            'Prairie',
            'Pulaski',
            'Randolph',
            'Saint Francis',
            'Saline',
            'Scott',
            'Searcy',
            'Sebastian',
            'Sevier',
            'Sharp',
            'Stone',
            'Union',
            'Van Buren',
            'Washington',
            'White',
            'Woodruff',
            'Yell']

start_county = 0
end_county = 74
# Handle command line arguments 
argv = sys.argv
argv_len = len(argv)

if argv_len == 2:
    start_county = argv[1]
elif argv_len == 3:
    start_county = argv[1]
    end_county = argv[2]

for i in range (start_county, end_county):
    print('Script will check licenses from ' + counties[i] + ' County to ' + counties[end_county] + ' County')
    select_licenses_by_county(counties[i])

cat_outputs()