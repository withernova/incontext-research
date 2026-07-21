# Rejection-linked low-IoU bbox audit

- samples: 140
- identification TP IoU<0.1: 35
- identification TP IoU<0.5: 44
- negative No and candidate IoU>=0.5: 82/140

> Cross-image normalized geometry does not establish identity or visual-content similarity.

## all_positive (n=140)
- paired_negative_prediction: paired corner-RMSE=0.245293; same-class-other=0.210331; delta=0.034962; paired-closer=0.400; permutation p(lower)=0.999900
- paired_negative_annotation: paired corner-RMSE=0.249264; same-class-other=0.212340; delta=0.036925; paired-closer=0.357; permutation p(lower)=0.999500

## identification_tp (n=133)
- paired_negative_prediction: paired corner-RMSE=0.244641; same-class-other=0.209318; delta=0.035322; paired-closer=0.391; permutation p(lower)=0.999800
- paired_negative_annotation: paired corner-RMSE=0.247131; same-class-other=0.214406; delta=0.032725; paired-closer=0.361; permutation p(lower)=0.996900

## tp_iou_lt_0.5 (n=44)
- paired_negative_prediction: paired corner-RMSE=0.280527; same-class-other=0.235500; delta=0.045027; paired-closer=0.341; permutation p(lower)=0.977702
- paired_negative_annotation: paired corner-RMSE=0.281593; same-class-other=0.251269; delta=0.030324; paired-closer=0.341; permutation p(lower)=0.839116

## tp_iou_lt_0.1 (n=35)
- paired_negative_prediction: paired corner-RMSE=0.288008; same-class-other=0.252680; delta=0.035328; paired-closer=0.400; permutation p(lower)=0.918008
- paired_negative_annotation: paired corner-RMSE=0.292365; same-class-other=0.277180; delta=0.015185; paired-closer=0.429; permutation p(lower)=0.663734

## Continuous
- rho(pos IoU, distance to paired negative prediction)=-0.218305
- rho(pos IoU, distance to paired negative annotation)=-0.221425
