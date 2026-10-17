
undefined8 FUN_01033f80(undefined8 *param_1,uint param_2)

{
  char cVar1;
  undefined8 uVar2;
  code *pcVar3;
  long lVar4;
  undefined *puVar5;
  undefined1 uVar6;
  long lVar7;
  long local_48 [2];
  long local_38;
  
  lVar4 = DAT_02693df8;
  local_38 = *DAT_01a1f100;
  uVar6 = 0;
  if (0x899a85 < param_2) {
    if (param_2 != 0x899a86) goto LAB_010340fc;
    puVar5 = (undefined *)0x2748;
LAB_010340e6:
    puVar5 = puVar5 + DAT_02693df8;
    uVar2 = *(undefined8 *)*param_1;
LAB_010340ef:
    FUN_000a1340(uVar2,puVar5,1);
    uVar6 = 1;
    goto LAB_010340fc;
  }
  if (0x891511 < param_2) {
    if (param_2 != 0x891512) goto LAB_010340fc;
    lVar4 = 0x2960;
LAB_01034082:
    FUN_000a2230(*(undefined8 *)*param_1,lVar4 + DAT_02693df8);
    uVar6 = 1;
    goto LAB_010340fc;
  }
  if (0x885e1a < param_2) {
    if (param_2 != 0x885e1b) goto LAB_010340fc;
    puVar5 = (undefined *)0xa58;
    goto LAB_010340e6;
  }
  if (0x87a609 < param_2) {
    if (param_2 != 0x87a60a) goto LAB_010340fc;
    pcVar3 = (code *)&PTR_DAT_00001f78;
    goto LAB_010340bf;
  }
  if (0x85ed78 < param_2) {
    if (param_2 != 0x85ed79) goto LAB_010340fc;
    puVar5 = (undefined *)0xa63;
    goto LAB_010340e6;
  }
  if (param_2 < 0x8774) {
    if (param_2 - 100 < 0x483) {
                    /* WARNING: Could not recover jumptable at 0x01034007. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      uVar2 = (*(code *)(&LAB_0103c988 + *(int *)(&LAB_0103c988 + (ulong)(param_2 - 100) * 4)))();
      return uVar2;
    }
    goto LAB_010340fc;
  }
  if (param_2 < 0x26587) {
    if (param_2 != 0x8774) goto LAB_010340fc;
    param_1 = (undefined8 *)*param_1;
    FUN_000a2180(*param_1,&DAT_000022a0 + DAT_02693df8);
    FUN_000a2180(*param_1,&DAT_000022a4 + lVar4);
    FUN_000a2180(*param_1,&DAT_000022a8 + lVar4);
    FUN_000a2180(*param_1,&DAT_000022ac + lVar4);
    FUN_000a2180(*param_1,&DAT_000022b0 + lVar4);
    FUN_000a2180(*param_1,&DAT_000022b4 + lVar4);
    pcVar3 = (code *)(&DAT_000022b8 + lVar4);
    goto LAB_0103c904;
  }
  if (param_2 < 0x4ee33) {
    if (param_2 != 0x26587) goto LAB_010340fc;
    puVar5 = (undefined *)0xa6f;
    goto LAB_010340e6;
  }
  if (param_2 < 0x60203) {
    if (param_2 != 0x4ee33) goto LAB_010340fc;
    pcVar3 = (code *)0x2688;
LAB_010340bf:
    pcVar3 = (code *)((long)pcVar3 + DAT_02693df8);
    uVar2 = *(undefined8 *)*param_1;
  }
  else {
    if (param_2 < 0x69222) {
      if (param_2 != 0x60203) goto LAB_010340fc;
      pcVar3 = (code *)&DAT_00002360;
      goto LAB_010340bf;
    }
    if (0x85355d < param_2) {
      if (param_2 != 0x85355e) goto LAB_010340fc;
      puVar5 = &DAT_00002365;
      goto LAB_010340e6;
    }
    if (0x85095d < param_2) {
      if (param_2 != 0x85095e) goto LAB_010340fc;
      pcVar3 = (code *)0x248c;
      goto LAB_010340bf;
    }
    if (0x82e1d7 < param_2) {
      if (param_2 != 0x82e1d8) goto LAB_010340fc;
      param_1 = (undefined8 *)*param_1;
      FUN_000a2180(*param_1,&DAT_00001f38 + DAT_02693df8);
      FUN_000a2180(*param_1,&DAT_00001f3c + lVar4);
      FUN_000a2180(*param_1,&LAB_00001f40 + lVar4);
      FUN_000a2180(*param_1,lVar4 + 0x1f44);
      pcVar3 = (code *)((long)&PTR_DAT_00001f48 + lVar4);
      goto LAB_0103c904;
    }
    if (0x82b30e < param_2) {
      if (param_2 == 0x82b30f) {
        lVar7 = DAT_02693df8 + 0xa74;
        param_1 = (undefined8 *)*param_1;
        lVar4 = 0;
        uVar6 = 1;
        do {
          FUN_000a2180(*param_1,lVar7 + lVar4);
          lVar4 = lVar4 + 4;
        } while ((int)lVar4 != 0x50);
      }
      goto LAB_010340fc;
    }
    if (0x82359c < param_2) {
      if (param_2 != 0x82359d) goto LAB_010340fc;
      pcVar3 = (code *)0x2468;
      goto LAB_010340bf;
    }
    if (0x81f408 < param_2) {
      if (param_2 != 0x81f409) goto LAB_010340fc;
      puVar5 = (undefined *)0xf80;
      goto LAB_010340e6;
    }
    if (0x81b5b5 < param_2) {
      if (param_2 != 0x81b5b6) goto LAB_010340fc;
      param_1 = (undefined8 *)*param_1;
      FUN_000a1340(*param_1,DAT_02693df8 + 0xcb4,1);
      FUN_000a1340(*param_1,lVar4 + 0xcb5,1);
      FUN_000a1340(*param_1,lVar4 + 0xcb6,1);
      FUN_000a1340(*param_1,lVar4 + 0xcb7,1);
      FUN_000a1340(*param_1,lVar4 + 0xcb8,1);
      FUN_000a1340(*param_1,lVar4 + 0xcb9,1);
      FUN_000a1340(*param_1,lVar4 + 0xcba,1);
      puVar5 = (undefined *)(lVar4 + 0xcbb);
LAB_0103c78a:
      uVar2 = *param_1;
      goto LAB_010340ef;
    }
    if (0x804dbd < param_2) {
      if (param_2 != 0x804dbe) goto LAB_010340fc;
      param_1 = (undefined8 *)*param_1;
      FUN_000a2180(*param_1,DAT_02693df8 + 0x25a4);
      FUN_000a2180(*param_1,&DAT_000025a8 + lVar4);
      FUN_000a2180(*param_1,&DAT_000025ac + lVar4);
      FUN_000a2180(*param_1,FUN_000025b0 + lVar4);
      FUN_000a2180(*param_1,lVar4 + 0x25b4);
      FUN_000a2180(*param_1,lVar4 + 0x25b8);
      FUN_000a2180(*param_1,lVar4 + 0x25bc);
      pcVar3 = (code *)(lVar4 + 0x25c0);
      goto LAB_0103c904;
    }
    if (param_2 < 0x6aa77) {
      if (param_2 != 0x69222) goto LAB_010340fc;
      pcVar3 = (code *)0x3210;
      goto LAB_010340bf;
    }
    if (param_2 < 0x82dd8) {
      if (param_2 != 0x6aa77) goto LAB_010340fc;
      param_1 = (undefined8 *)*param_1;
      FUN_000a1340(*param_1,DAT_02693df8 + 0xcd4,1);
      FUN_000a1340(*param_1,lVar4 + 0xcd5,1);
      FUN_000a1340(*param_1,lVar4 + 0xcd6,1);
      FUN_000a1340(*param_1,lVar4 + 0xcd7,1);
      FUN_000a1340(*param_1,lVar4 + 0xcd8,1);
      FUN_000a1340(*param_1,lVar4 + 0xcd9,1);
      FUN_000a1340(*param_1,lVar4 + 0xcda,1);
      puVar5 = (undefined *)(lVar4 + 0xcdb);
      goto LAB_0103c78a;
    }
    if (param_2 < 0x92e8b) {
      if (param_2 != 0x82dd8) goto LAB_010340fc;
      pcVar3 = (code *)0x2488;
      goto LAB_010340bf;
    }
    if (0xc406e < param_2) {
      if (param_2 < 0xc6838) {
        if (param_2 != 0xc406f) goto LAB_010340fc;
        puVar5 = (undefined *)0xa64;
        goto LAB_010340e6;
      }
      if (param_2 < 0xceb6a) {
        if (param_2 != 0xc6838) goto LAB_010340fc;
        pcVar3 = (code *)0x24b0;
        goto LAB_010340bf;
      }
      if (param_2 < 0xd33ba) {
        if (param_2 != 0xceb6a) goto LAB_010340fc;
        param_1 = (undefined8 *)*param_1;
        FUN_000a2180(*param_1,&DAT_00001f10 + DAT_02693df8);
        FUN_000a2180(*param_1,lVar4 + 0x1f14);
        FUN_000a2180(*param_1,&DAT_00001f18 + lVar4);
        FUN_000a2180(*param_1,&DAT_00001f1c + lVar4);
        pcVar3 = (code *)(&DAT_00001f20 + lVar4);
        goto LAB_0103c904;
      }
      if (param_2 < 0xd7732) {
        if (param_2 != 0xd33ba) goto LAB_010340fc;
        puVar5 = &DAT_00002364;
        goto LAB_010340e6;
      }
      if (param_2 < 0xe1295) {
        if (param_2 != 0xd7732) goto LAB_010340fc;
        pcVar3 = (code *)0xa68;
      }
      else if (param_2 < 0xe8331) {
        if (param_2 != 0xe1295) goto LAB_010340fc;
        pcVar3 = (code *)0xc88;
      }
      else {
        if (0x7e8240 < param_2) {
          if (param_2 != 0x7e8241) goto LAB_010340fc;
          puVar5 = (undefined *)0x59a;
          goto LAB_010340e6;
        }
        if (param_2 < 0x7e71c2) {
          if (0x7c0de8 < param_2) {
            if (param_2 != 0x7c0de9) goto LAB_010340fc;
            lVar4 = 0x217c;
LAB_0103ba9c:
            FUN_0103e280(*param_1,lVar4 + DAT_02693df8);
            uVar6 = 1;
            goto LAB_010340fc;
          }
          if (0x7a3248 < param_2) {
            if (param_2 != 0x7a3249) goto LAB_010340fc;
            lVar4 = 0x220c;
LAB_0103c25e:
            FUN_0103e160(*param_1,lVar4 + DAT_02693df8);
            uVar6 = 1;
            goto LAB_010340fc;
          }
          if (0x78439a < param_2) {
            if (param_2 != 0x78439b) goto LAB_010340fc;
            puVar5 = (undefined *)0xa62;
            goto LAB_010340e6;
          }
          if (param_2 < 0x77615a) {
            if (param_2 < 0x775aa7) {
              if (param_2 < 0x76e450) {
                if (0x76a4c1 < param_2) {
                  if (param_2 != 0x76a4c2) goto LAB_010340fc;
                  puVar5 = (undefined *)0xa6d;
                  goto LAB_010340e6;
                }
                if (0x719937 < param_2) {
                  if (param_2 == 0x719938) {
                    FUN_0103e070(*param_1,&DAT_00002367 + DAT_02693df8);
                    uVar6 = 1;
                  }
                  goto LAB_010340fc;
                }
                if (0x716b1b < param_2) {
                  if (param_2 != 0x716b1c) goto LAB_010340fc;
                  lVar4 = 0x21bc;
                  goto LAB_0103ba9c;
                }
                if (param_2 < 0x7079f2) {
                  if (param_2 < 0x704cb4) {
                    if (0x6c62a2 < param_2) {
                      if (param_2 != 0x6c62a3) goto LAB_010340fc;
                      puVar5 = (undefined *)0xa6e;
                      goto LAB_010340e6;
                    }
                    if (param_2 < 0x6b138d) {
                      if (0x6a11ea < param_2) {
                        if (param_2 != 0x6a11eb) goto LAB_010340fc;
                        param_1 = (undefined8 *)*param_1;
                        FUN_000a2180(*param_1,DAT_02693df8 + 0x2694);
                        FUN_000a2180(*param_1,lVar4 + 0x2698);
                        FUN_000a2180(*param_1,lVar4 + 0x269c);
                        FUN_000a2180(*param_1,lVar4 + 0x26a0);
                        FUN_000a2180(*param_1,lVar4 + 0x26a4);
                        FUN_000a2180(*param_1,lVar4 + 0x26a8);
                        FUN_000a2180(*param_1,lVar4 + 0x26ac);
                        pcVar3 = (code *)(lVar4 + 0x26b0);
                        goto LAB_0103c904;
                      }
                      if (param_2 < 0x64ae2d) {
                        if (param_2 < 0x611f17) {
                          if (param_2 < 0x60cf7f) {
                            if (param_2 < 0x5e2395) {
                              if (0x5d342f < param_2) {
                                if (param_2 == 0x5d3430) {
                                  lVar7 = DAT_02693df8 + 0x970;
                                  param_1 = (undefined8 *)*param_1;
                                  lVar4 = 0;
                                  uVar6 = 1;
                                  do {
                                    FUN_000a2180(*param_1,lVar7 + lVar4);
                                    lVar4 = lVar4 + 4;
                                  } while ((int)lVar4 != 100);
                                }
                                goto LAB_010340fc;
                              }
                              if (0x5a9f16 < param_2) {
                                if (param_2 != 0x5a9f17) goto LAB_010340fc;
                                pcVar3 = FUN_00001fd0;
                                goto LAB_0103c927;
                              }
                              if (param_2 < 0xe8964) {
                                if (param_2 == 0xe8331) {
                                  lVar7 = DAT_02693df8 + 0x25c4;
                                  param_1 = (undefined8 *)*param_1;
                                  lVar4 = 0;
                                  uVar6 = 1;
                                  do {
                                    cVar1 = FUN_000a1490(*param_1,local_48);
                                    if (cVar1 != '\0') {
                                      FUN_000a1340(*param_1,lVar7 + lVar4,local_48[0]);
                                      *(undefined1 *)(lVar7 + local_48[0] + lVar4) = 0;
                                    }
                                    lVar4 = lVar4 + 0x18;
                                  } while ((int)lVar4 != 0xc0);
                                }
                                goto LAB_010340fc;
                              }
                              if (param_2 < 0xf1048) {
                                if (param_2 != 0xe8964) goto LAB_010340fc;
                                pcVar3 = (code *)0x247c;
                              }
                              else {
                                if (param_2 < 0xf71e5) {
                                  if (param_2 != 0xf1048) goto LAB_010340fc;
                                  puVar5 = (undefined *)0x598;
                                  goto LAB_010340e6;
                                }
                                if (param_2 < 0x5a62f7) {
                                  if (param_2 < 0x5a60e1) {
                                    if (param_2 < 0x5a17d6) {
                                      if (param_2 < 0x59ec37) {
                                        if (param_2 < 0x58e0a3) {
                                          if (0x566452 < param_2) {
                                            if (param_2 != 0x566453) goto LAB_010340fc;
                                            lVar4 = 0x2958;
                                            goto LAB_01034082;
                                          }
                                          if (0x55a2ea < param_2) {
                                            if (param_2 != 0x55a2eb) goto LAB_010340fc;
                                            pcVar3 = (code *)0x1f80;
LAB_0103c927:
                                            FUN_0103e280(*param_1,pcVar3 + DAT_02693df8);
                                            uVar6 = 1;
                                            goto LAB_010340fc;
                                          }
                                          if (0x54c532 < param_2) {
                                            if (param_2 != 0x54c533) goto LAB_010340fc;
                                            param_1 = (undefined8 *)*param_1;
                                            FUN_000a2180(*param_1,DAT_02693df8 + 0xc94);
                                            FUN_000a2180(*param_1,lVar4 + 0xc98);
                                            FUN_000a2180(*param_1,lVar4 + 0xc9c);
                                            FUN_000a2180(*param_1,lVar4 + 0xca0);
                                            FUN_000a2180(*param_1,lVar4 + 0xca4);
                                            FUN_000a2180(*param_1,lVar4 + 0xca8);
                                            FUN_000a2180(*param_1,lVar4 + 0xcac);
                                            pcVar3 = (code *)(lVar4 + 0xcb0);
                                            goto LAB_0103c904;
                                          }
                                          if (param_2 < 0x50e95b) {
                                            if (0x505d41 < param_2) {
                                              if (param_2 != 0x505d42) goto LAB_010340fc;
                                              puVar5 = (undefined *)0xc91;
                                              goto LAB_010340e6;
                                            }
                                            if (param_2 < 0x4feaf2) {
                                              if (param_2 < 0x4f0f31) {
                                                if (0x4e997b < param_2) {
                                                  if (param_2 != 0x4e997c) goto LAB_010340fc;
                                                  puVar5 = (undefined *)0xf81;
                                                  goto LAB_010340e6;
                                                }
                                                if (param_2 < 0x4e7117) {
                                                  if (0x4e324d < param_2) {
                                                    if (param_2 != 0x4e324e) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x2010;
                                                    goto LAB_0103c927;
                                                  }
                                                  if (param_2 < 0x4ac72b) {
                                                    if (param_2 < 0x48b677) {
                                                      if (param_2 < 0x465ff5) {
                                                        if (0x441f54 < param_2) {
                                                          if (param_2 != 0x441f55)
                                                          goto LAB_010340fc;
                                                          lVar4 = 0x21fc;
                                                          goto LAB_0103c25e;
                                                        }
                                                        if (param_2 < 0x4409ec) {
                                                          if (param_2 < 0x437e73) {
                                                            if (0x434dfd < param_2) {
                                                              if (param_2 != 0x434dfe)
                                                              goto LAB_010340fc;
                                                              param_1 = (undefined8 *)*param_1;
                                                              FUN_000a1340(*param_1,DAT_02693df8 +
                                                                                    0xcc4,1);
                                                              FUN_000a1340(*param_1,lVar4 + 0xcc5,1)
                                                              ;
                                                              FUN_000a1340(*param_1,lVar4 + 0xcc6,1)
                                                              ;
                                                              FUN_000a1340(*param_1,lVar4 + 0xcc7,1)
                                                              ;
                                                              FUN_000a1340(*param_1,lVar4 + 0xcc8,1)
                                                              ;
                                                              FUN_000a1340(*param_1,lVar4 + 0xcc9,1)
                                                              ;
                                                              FUN_000a1340(*param_1,lVar4 + 0xcca,1)
                                                              ;
                                                              puVar5 = (undefined *)(lVar4 + 0xccb);
                                                              goto LAB_0103c78a;
                                                            }
                                                            if (param_2 < 0x417f37) {
                                                              if (param_2 < 0x3eeae3) {
                                                                if (param_2 < 0x3b1996) {
                                                                  if (param_2 < 0x398db7) {
                                                                    if (param_2 < 0x38ea36) {
                                                                      if (param_2 < 0x362ecc) {
                                                                        if (0x3204f5 < param_2) {
                                                                          if (param_2 != 0x3204f6)
                                                                          goto LAB_010340fc;
                                                                          pcVar3 = (code *)0x2090;
                                                                          goto LAB_0103c927;
                                                                        }
                                                                        if (param_2 < 0x309a73) {
                                                                          if (param_2 < 0x2fbcec) {
                                                                            if (0x2f1078 < param_2)
                                                                            {
                                                                              if (param_2 !=
                                                                                  0x2f1079)
                                                                              goto LAB_010340fc;
                                                                              puVar5 = (undefined *)
                                                                                       0xac5;
                                                                              goto LAB_010340e6;
                                                                            }
                                                                            if (0x2e0ec9 < param_2)
                                                                            {
                                                                              if (param_2 ==
                                                                                  0x2e0eca) {
                                                                                FUN_000a1340(*(
                                                  undefined8 *)*param_1,DAT_02693df8 + 0x332d,1);
                                                  uVar6 = 1;
                                                  }
                                                  goto LAB_010340fc;
                                                  }
                                                  if (param_2 < 0x27e6ab) {
                                                    if (param_2 < 0x26841b) {
                                                      if (0x250165 < param_2) {
                                                        if (param_2 != 0x250166) goto LAB_010340fc;
                                                        puVar5 = (undefined *)0x2684;
                                                        goto LAB_010340e6;
                                                      }
                                                      if (param_2 < 0x22e0e5) {
                                                        if (param_2 < 0x2218a5) {
                                                          if (param_2 < 0x216f98) {
                                                            if (param_2 < 0x1fd6ec) {
                                                              if (param_2 < 0x1f6b39) {
                                                                if (param_2 < 0x1ea372) {
                                                                  if (0x1dc160 < param_2) {
                                                                    if (param_2 != 0x1dc161)
                                                                    goto LAB_010340fc;
                                                                    param_1 = (undefined8 *)*param_1
                                                                    ;
                                                                    FUN_000a1340(*param_1,
                                                  DAT_02693df8 + 0xcdc,1);
                                                  FUN_000a1340(*param_1,lVar4 + 0xcdd,1);
                                                  FUN_000a1340(*param_1,lVar4 + 0xcde,1);
                                                  FUN_000a1340(*param_1,lVar4 + 0xcdf,1);
                                                  FUN_000a1340(*param_1,lVar4 + 0xce0,1);
                                                  FUN_000a1340(*param_1,lVar4 + 0xce1,1);
                                                  FUN_000a1340(*param_1,lVar4 + 0xce2,1);
                                                  puVar5 = (undefined *)(lVar4 + 0xce3);
                                                  goto LAB_0103c78a;
                                                  }
                                                  if (param_2 < 0x1d0476) {
                                                    if (param_2 < 0x1a8d46) {
                                                      if (param_2 < 0x1a39e5) {
                                                        if (param_2 < 0x185f0d) {
                                                          if (param_2 < 0x17f073) {
                                                            if (0x17898c < param_2) {
                                                              if (param_2 == 0x17898d) {
                                                                FUN_0103e160(*param_1,DAT_02693df8 +
                                                                                      0x1fc0);
                                                                uVar6 = 1;
                                                              }
                                                              goto LAB_010340fc;
                                                            }
                                                            if (param_2 < 0x170fd7) {
                                                              if (0x170226 < param_2) {
                                                                if (param_2 != 0x170227)
                                                                goto LAB_010340fc;
                                                                puVar5 = (undefined *)0xa60;
                                                                goto LAB_010340e6;
                                                              }
                                                              if (param_2 < 0x14bbd7) {
                                                                if (0x13268a < param_2) {
                                                                  if (param_2 != 0x13268b)
                                                                  goto LAB_010340fc;
                                                                  param_1 = (undefined8 *)*param_1;
                                                                  FUN_000a2180(*param_1,&
                                                  DAT_00001f60 + DAT_02693df8);
                                                  FUN_000a2180(*param_1,lVar4 + 0x1f64);
                                                  FUN_000a2180(*param_1,&DAT_00001f68 + lVar4);
                                                  FUN_000a2180(*param_1,&DAT_00001f6c + lVar4);
                                                  pcVar3 = FUN_00001f70 + lVar4;
                                                  goto LAB_0103c904;
                                                  }
                                                  if (0x128e3b < param_2) {
                                                    if (param_2 != 0x128e3c) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x2050;
                                                    goto LAB_0103c927;
                                                  }
                                                  if (param_2 < 0x1217f5) {
                                                    if (param_2 != 0xf71e5) {
                                                      if (param_2 != 0xf725e) {
                                                        if (param_2 != 0xfd90f) goto LAB_010340fc;
                                                        puVar5 = (undefined *)0xa6c;
                                                        goto LAB_010340e6;
                                                      }
                                                      param_1 = (undefined8 *)*param_1;
                                                      FUN_000a2180(*param_1,&DAT_00001f24 +
                                                                            DAT_02693df8);
                                                      FUN_000a2180(*param_1,(long)&PTR_DAT_00001f28
                                                                            + lVar4);
                                                      FUN_000a2180(*param_1,lVar4 + 0x1f2c);
                                                      FUN_000a2180(*param_1,&DAT_00001f30 + lVar4);
                                                      pcVar3 = (code *)(&DAT_00001f34 + lVar4);
                                                      goto LAB_0103c904;
                                                    }
                                                    pcVar3 = (code *)0x2478;
                                                  }
                                                  else {
                                                    if (param_2 != 0x1217f5) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x268c;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x14bbd7) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x24a8;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x170fd7) goto LAB_010340fc;
                                                    pcVar3 = (code *)&DAT_000022bc;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x17f073) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x26c0;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x185f0d) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x24a4;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x1a39e5) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x3128;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x1a8d46) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x249c;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x1d0476) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x22c8;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x1ea372) goto LAB_010340fc;
                                                    pcVar3 = (code *)0xac8;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x1f6b39) goto LAB_010340fc;
                                                    pcVar3 = (code *)0xf84;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x1fd6ec) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x2470;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x216f98) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x2598;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x2218a5) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x2474;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x22e0e5) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x2494;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x26841b) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x2490;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x27e6ab) goto LAB_010340fc;
                                                    pcVar3 = (code *)&DAT_0000235c;
                                                  }
                                                  goto LAB_010340bf;
                                                  }
                                                  if (param_2 != 0x2fbcec) goto LAB_010340fc;
                                                  param_1 = (undefined8 *)*param_1;
                                                  FUN_000a1340(*param_1,DAT_02693df8 + 0xcbc,1);
                                                  FUN_000a1340(*param_1,lVar4 + 0xcbd,1);
                                                  FUN_000a1340(*param_1,lVar4 + 0xcbe,1);
                                                  FUN_000a1340(*param_1,lVar4 + 0xcbf,1);
                                                  FUN_000a1340(*param_1,lVar4 + 0xcc0,1);
                                                  FUN_000a1340(*param_1,lVar4 + 0xcc1,1);
                                                  FUN_000a1340(*param_1,lVar4 + 0xcc2,1);
                                                  puVar5 = (undefined *)(lVar4 + 0xcc3);
                                                  }
                                                  else {
                                                    if (param_2 != 0x309a73) goto LAB_010340fc;
                                                    param_1 = (undefined8 *)*param_1;
                                                    FUN_000a1340(*param_1,DAT_02693df8 + 0xccc,1);
                                                    FUN_000a1340(*param_1,lVar4 + 0xccd,1);
                                                    FUN_000a1340(*param_1,lVar4 + 0xcce,1);
                                                    FUN_000a1340(*param_1,lVar4 + 0xccf,1);
                                                    FUN_000a1340(*param_1,lVar4 + 0xcd0,1);
                                                    FUN_000a1340(*param_1,lVar4 + 0xcd1,1);
                                                    FUN_000a1340(*param_1,lVar4 + 0xcd2,1);
                                                    puVar5 = (undefined *)(lVar4 + 0xcd3);
                                                  }
                                                  goto LAB_0103c78a;
                                                  }
                                                  if (param_2 != 0x362ecc) goto LAB_010340fc;
                                                  pcVar3 = (code *)0xc8c;
                                                  }
                                                  else {
                                                    if (param_2 != 0x38ea36) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x22c4;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x398db7) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x22cc;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x3b1996) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x3284;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x3eeae3) goto LAB_010340fc;
                                                    pcVar3 = (code *)&DAT_00002358;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x417f37) goto LAB_010340fc;
                                                    pcVar3 = (code *)&DAT_00002354;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x437e73) goto LAB_010340fc;
                                                    pcVar3 = (code *)0x2a88;
                                                  }
                                                  goto LAB_010340bf;
                                                  }
                                                  if (param_2 != 0x4409ec) goto LAB_010340fc;
                                                  puVar5 = (undefined *)0x599;
                                                  }
                                                  else {
                                                    if (param_2 != 0x465ff5) goto LAB_010340fc;
                                                    puVar5 = (undefined *)0xa59;
                                                  }
                                                  }
                                                  else {
                                                    if (param_2 != 0x48b677) goto LAB_010340fc;
                                                    puVar5 = (undefined *)0x2366;
                                                  }
                                                  goto LAB_010340e6;
                                                  }
                                                  if (param_2 != 0x4ac72b) goto LAB_010340fc;
                                                  pcVar3 = (code *)0x1f7c;
                                                }
                                                else {
                                                  if (param_2 != 0x4e7117) goto LAB_010340fc;
                                                  pcVar3 = (code *)0x26b4;
                                                }
                                              }
                                              else {
                                                if (param_2 != 0x4f0f31) goto LAB_010340fc;
                                                pcVar3 = (code *)0x259c;
                                              }
                                            }
                                            else {
                                              if (param_2 != 0x4feaf2) goto LAB_010340fc;
                                              pcVar3 = FUN_000022c0;
                                            }
                                          }
                                          else {
                                            if (param_2 != 0x50e95b) goto LAB_010340fc;
                                            pcVar3 = (code *)0x2a94;
                                          }
                                        }
                                        else {
                                          if (param_2 != 0x58e0a3) goto LAB_010340fc;
                                          pcVar3 = (code *)0x25a0;
                                        }
                                        goto LAB_010340bf;
                                      }
                                      if (param_2 != 0x59ec37) goto LAB_010340fc;
                                      puVar5 = (undefined *)0xa61;
                                    }
                                    else {
                                      if (param_2 != 0x5a17d6) goto LAB_010340fc;
                                      puVar5 = (undefined *)0x2690;
                                    }
                                    goto LAB_010340e6;
                                  }
                                  if (param_2 != 0x5a60e1) goto LAB_010340fc;
                                  pcVar3 = (code *)0x26b8;
                                }
                                else {
                                  if (param_2 != 0x5a62f7) goto LAB_010340fc;
                                  pcVar3 = (code *)0x26bc;
                                }
                              }
                            }
                            else {
                              if (param_2 != 0x5e2395) goto LAB_010340fc;
                              pcVar3 = (code *)0xa5c;
                            }
                          }
                          else {
                            if (param_2 != 0x60cf7f) goto LAB_010340fc;
                            pcVar3 = (code *)0x3218;
                          }
                          goto LAB_010340bf;
                        }
                        if (param_2 != 0x611f17) goto LAB_010340fc;
                        puVar5 = (undefined *)0x2594;
                      }
                      else {
                        if (param_2 != 0x64ae2d) goto LAB_010340fc;
                        puVar5 = (undefined *)0xc90;
                      }
                      goto LAB_010340e6;
                    }
                    if (param_2 != 0x6b138d) goto LAB_010340fc;
                    pcVar3 = (code *)&DAT_00001f74;
                  }
                  else {
                    if (param_2 != 0x704cb4) goto LAB_010340fc;
                    pcVar3 = (code *)0x24ac;
                  }
                }
                else {
                  if (param_2 != 0x7079f2) goto LAB_010340fc;
                  pcVar3 = (code *)0x246c;
                }
              }
              else {
                if (param_2 != 0x76e450) goto LAB_010340fc;
                pcVar3 = (code *)0x24a0;
              }
            }
            else {
              if (param_2 != 0x775aa7) goto LAB_010340fc;
              pcVar3 = (code *)0x2a7c;
            }
          }
          else {
            if (param_2 != 0x77615a) goto LAB_010340fc;
            pcVar3 = (code *)0xa70;
          }
        }
        else {
          if (param_2 != 0x7e71c2) goto LAB_010340fc;
          pcVar3 = (code *)0x2498;
        }
      }
      goto LAB_010340bf;
    }
    if (param_2 != 0x92e8b) goto LAB_010340fc;
    param_1 = (undefined8 *)*param_1;
    FUN_000a2180(*param_1,DAT_02693df8 + 0x1f4c);
    FUN_000a2180(*param_1,&DAT_00001f50 + lVar4);
    FUN_000a2180(*param_1,lVar4 + 0x1f54);
    FUN_000a2180(*param_1,(long)&PTR_DAT_00001f58 + lVar4);
    pcVar3 = (code *)(lVar4 + 0x1f5c);
LAB_0103c904:
    uVar2 = *param_1;
  }
  FUN_000a2180(uVar2,pcVar3);
  uVar6 = 1;
LAB_010340fc:
  if (*DAT_01a1f100 != local_38) {
    uVar2 = thunk_FUN_012aa7f6();
    return uVar2;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar6);
}

