
# Define variables
PYTHON = python
SCRIPT1 = E:\Library Strategic Research - Intelligence\2024\ETL Pipeline Testyard\Stage1_GetScopusID.py
SCRIPT2 = E:\Library Strategic Research - Intelligence\2024\ETL Pipeline Testyard\Stage2_GetScivalData.py
SCRIPT3 = E:\Library Strategic Research - Intelligence\2024\ETL Pipeline Testyard\Stage3_Merge.py
SCRIPT4 = E:\Library Strategic Research - Intelligence\2024\ETL Pipeline Testyard\Stage4_Combine.py

# Default target
.PHONY: all
all: script1 script2 script3 script4
    @echo All Stages executed successfully.

# Target to execute script1
.PHONY: script1
script1:
    @echo Executing Stage 1 - Get Scopus ID...
    $(PYTHON) $(SCRIPT1)

# Target to execute script2
.PHONY: script2
script2:
    @echo Executing Stage 2 - Get Scival Metrics...
    $(PYTHON) $(SCRIPT2)

# Target to execute script3
.PHONY: script3
script3:
    @echo Executing Stage 3 - Merge Scival Data with Input File...
    $(PYTHON) $(SCRIPT3)

# Target to execute script4
.PHONY: script4
script4:
    @echo Executing Stage 4 - Combine Stage 3 Output with No Scopus ID Data file...
    $(PYTHON) $(SCRIPT4)

