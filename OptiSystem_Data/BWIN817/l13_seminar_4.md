# Final scorecard production

- The final scorecards are then produced by running the same initial characteristic analysis and statistical algorithms on the
post inferred dataset, to generate the final set of characteristics for the
scorecard.
- not limited to the characteristics selected in the preliminary scorecard in this phase.
- the process of selecting characteristics needs to be repeated
# Scaling
- Scaling refers to the range and format of scores in a scorecard and the rate of change in odds for increases in score.
- Scorecard scores can take several
forms: score is the good/bad odd or probability, some defined numerical minimum/maximum scale with a specified odds ratio and specified rate of change of odds
- Scaling does not affect the predictive strength of the
scorecard
- The considerations of scaling are: Implementability of the scorecard, Ease of understanding, Continuity with existing scorecards or other scorecards in the
company.
- the relationship between odds and scores can be presented as a linear transformation: Score = Offset + Factor ln (odds)
- the scorecard is being developed using specified odds at a score and specified "points to double the odds" (pdo)
- Solving the equations for pdo, we get
pdo = Factor * In (2), therefore
Factor = pdo / In (2)
Offset = Score - {Factor * In (Odds)}
- Scaled score (for bin level i, variable j )= - (WOE of bin level i, variable j *
Coeff_woe variable j + Intercept / number_of_variables) * Factor +
(offset/number of variables)

