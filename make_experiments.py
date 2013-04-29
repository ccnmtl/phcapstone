#!/usr/bin/env python
import os

experiment_template = """<?xml version="1.0" encoding="us-ascii"?>
<!DOCTYPE experiments SYSTEM "behaviorspace.dtd">
<experiments>
  <experiment name="EXPERIMENT_NAME" repetitions="1" runMetricsEveryStep="true">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="STEPS"/>
    <metric>METRIC</metric>
    VARIABLES
    <enumeratedValueSet variable="number-of-nodes">
      <value value="494"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="base-output-sigma">
      <value value="5"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="base-output-mean">
      <value value="100"/>
    </enumeratedValueSet>
  </experiment>
</experiments>
"""

varied_template = """
    <steppedValueSet variable="VARIABLE_NAME" first="MIN" step="STEP" last="MAX"/>
"""
fixed_template = """
    <enumeratedValueSet variable="VARIABLE_NAME">
      <value value="VALUE"/>
    </enumeratedValueSet>
"""



number_of_nodes = 494
steps = 200
metric = "mean [mass] of turtles"

gammas = ["gamma1", "gamma2", "gamma3", "gamma4", "gamma5", "gamma6"]
sigmas = ["sigma1", "sigma2"]
alphas = ["food-exposure-alpha", "food-literacy-alpha",
          "food-convenience-alpha", "food-advertising-alpha",
          "domestic-activity-alpha", "recreation-activity-alpha"]
lambdas = ["food-exposure-lambda", "food-literacy-lambda",
          "food-convenience-lambda", "food-advertising-lambda",
          "domestic-activity-lambda", "recreation-activity-lambda"]

# default, min, step, max
gamma_specs = ("1", "1", "1", "10")
sigma_specs = ("5", "1", "1", "10")
alpha_specs = ("2", "1", "1", "10")
lambda_specs = ("0.5", "0.1", "0.1", "1")

all_vars = []
for g in gammas:
    all_vars.append((g, gamma_specs))

for s in sigmas:
    all_vars.append((s, sigma_specs))

for a in alphas:
    all_vars.append((a, alpha_specs))

for l in lambdas:
    all_vars.append((l, lambda_specs))

for(i, (v1, (v1_default, v1_min, v1_step, v1_max))) in enumerate(all_vars):
    for j in range(i + 1, len(all_vars)):
        v2, (v2_default, v2_min, v2_step, v2_max) = all_vars[j]
        filename = "%s-%s.xml" % (v1, v2)
        csv_filename = "%s-%s.csv" % (v1, v2)
        title = "%s/%s" % (v1, v2)
        vs1 = (
            varied_template.replace('VARIABLE_NAME', v1)
            .replace('MIN', v1_min)
            .replace('STEP', v1_step)
            .replace('MAX', v1_max))
        vs2 = (
            varied_template.replace('VARIABLE_NAME', v2)
            .replace('MIN', v2_min)
            .replace('STEP', v2_step)
            .replace('MAX', v2_max))
        variable_elements = [vs1, vs2]
        for (v, (d, mn, st, mx)) in all_vars:
            if v == v1 or v == v2:
                continue
            chunk = (fixed_template.replace('VARIABLE_NAME', v)
                     .replace('VALUE', d))
            variable_elements.append(chunk)
        variables_string = "".join(variable_elements)
        output = (
            experiment_template.replace(
                "EXPERIMENT_NAME", title)
            .replace('STEPS', str(steps))
            .replace('METRIC', metric)
            .replace('VARIABLES', variables_string))
        with open("experiments/%s" % filename, "wb") as xmlfile:
            xmlfile.write(output)
        command = (
            "java -Djava.library.path=./lib "
            "-Djava.ext.dirs= -XX:MaxPermSize=128m -Xmx1024m "
            "-Dfile.encoding=UTF-8 -cp ../netlogo-5.0.2/NetLogo.jar"
            " org.nlogo.headless.Main --model "
            "model.logo --setup-file "
            "experiments/%s "
            "--spreadsheet output/%s") % (filename, csv_filename)
        print command
        os.system(command)
        curl_cmd = "curl -F datafile=@output/%s http://localhost:8000/bs/add/" % csv_filename
        os.system(curl_cmd)
