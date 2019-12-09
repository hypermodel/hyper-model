FROM growingdata/hypermodel-base:buster-0.1.80

RUN pip install --upgrade pip

# Install postgres (required by the singet tap / target)
RUN apt-get update \
    && apt-get install -qq -y wget ca-certificates gnupg2 build-essential git

# RUN bash -c "echo deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main >> /etc/apt/sources.list.d/pgdg.list"
# RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

# RUN apt-get update \
#     && apt-get install -qq -y postgresql-11 postgresql-contrib libpq-dev

# RUN apt-get install -qq -y  python-psycopg2
# # Taps for common databases
# RUN pip install tap-mysql tap-redshift tap-postgres 

# # Targets (whoah, there are a lot missing here!)
# RUN pip install singer-target-postgres target-csv

# # Taps for SaaS
# RUN pip install \
#     tap-google-analytics \
#     tap-linkedin-ads \
#     tap-jira \
#     tap-facebook \
#     tap-slack 


WORKDIR /repos

RUN git clone https://github.com/GrowingData/target-bigquery.git \
    && cd target-bigquery \
    && pip install -e .

WORKDIR /repos
RUN git clone https://github.com/GrowingData/tap-nikabot.git \
    && cd tap-nikabot \
    && pip install -e .

WORKDIR /repos
RUN git clone https://github.com/GrowingData/tap-xero.git \
    && cd tap-xero \
    && pip install -e .


