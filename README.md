# AirbnbHostListings
The dataset describes the listing activity and metrics in NYC, NY for 2019. The format of the data is Comma Separated Values (.csv file) and contains 48896 rows. My aim here is to 
1. Predict the prices of house listings on the bases of the listing information. 
2. Determine the popularity based on geographic locations, room types, number of review and availability.
3. Analyze the most frequently used words in the listing names and their correlation with the number of reviews and neighborhood groups.

Variable Name	Data Type	Variable Description
id	Num	Unique record identification number
name	Num	Indicates the names of the listed house
host_id Num	Identification number associates with each host
host_name	Num	Name of the hosts who have listed houses for airbnb
neighbourhood_group	Num	Division of New York into 5 neighbourhood groups.
neighbourhood	Num	Different neighbourhoods associated with each neighbourhood group (221 groups)
latitude	Num	Indicates the latitude of each house listing
longitude	Num	Indicates the longitude of each house listing
room_type Num	Room categories associated with each house listing (3 categories)
price	Char	Price of each house listing
minimum_nights	Char	Minimum number of nights that a listing can be booked for
number_of_reviews	Char	Count of reviews associated with each house listing
last_review	Num	Date of the last review posted for individual listings
reviews_per_month	Num	Average number of reviews posted for individual listings per month
calculated_host_listings_count	Num	Number of listings posted by each host
availability_365 Num	Current availability of each house listing in days
