FROM python:3.9
MAINTAINER Leopold Talirz <leopold.talirz@gmail.com>

# Copy app
WORKDIR /app/isotherm-digitizer
COPY digitizer ./digitizer
COPY setup.py README.md .
RUN pip install --user --no-warn-script-location -e .

# start panel server
# this is where the panel script is placed
ENV PATH="${PATH}:/root/.local/bin"
EXPOSE 5006
CMD ["panel", "serve", "digitizer", "--use-xheaders"]
#CMD ["/bin/sleep", "1000"]

#EOF
