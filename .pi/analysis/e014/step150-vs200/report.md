# E-014 step150 与 step200 配对分析

同轮1766条逐dataset_index/id/dataset/target对齐。step150 Selected .6932669712 Oracle .7263236003 多框263/1766；step200 Selected .6916960158 Oracle .7573992982 多框791/1766。single→multi n528 Selected .6204368738→.5962361197 Oracle .6204368738→.7192414999；multi→multi n260 Selected .5840363228→.6465473505。Oracle命中但Selected失败67→133；150多框全零score84/263，失败中top tie29/67。最后50步候选覆盖改善但整体选框持平，不能断言显著退化或奖励因果。未做图像人工复核、显著性检验；未测试，无Solid/Claim提升。

来源：e014-discovery-score04-step150-eval1766-20261015T161128Z；e014-discovery-score04-step200-eval1766-20261015T152856Z。
