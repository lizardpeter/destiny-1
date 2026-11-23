
void FUN_002b4af0(long param_1)

{
  long lVar1;
  char cVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  long lVar6;
  bool bVar7;
  undefined1 local_3300 [64];
  undefined4 local_32c0;
  undefined1 local_32bb;
  undefined1 local_327a;
  undefined1 local_3239;
  undefined1 local_31f8;
  undefined1 local_31b7;
  undefined1 local_3176;
  undefined1 local_3135;
  undefined1 local_30f4;
  undefined1 local_30b3;
  undefined1 local_3072;
  undefined1 local_3030;
  undefined4 local_2ff0;
  undefined1 local_2feb;
  undefined1 local_2faa;
  undefined1 local_2f69;
  undefined1 local_2f28;
  undefined1 local_2ee7;
  undefined1 local_2ea6;
  undefined1 local_2e65;
  undefined1 local_2e24;
  undefined1 local_2de3;
  undefined1 local_2da2;
  int local_2d38;
  undefined1 auStack_2d34 [5380];
  undefined1 local_1830 [10];
  undefined1 local_1826;
  undefined1 local_1626 [22];
  undefined4 local_1610;
  undefined1 local_10c;
  undefined1 local_df;
  undefined1 local_9f;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (*(char *)(param_1 + 0x27d) == '\0') {
    cVar2 = FUN_002ba0a0(param_1);
    if (cVar2 == '\0') {
      lVar6 = param_1 + 0x90;
      cVar2 = FUN_002ba0a0(lVar6);
      if (cVar2 == '\0') {
        lVar1 = param_1 + 0x128;
        cVar2 = FUN_002ba0a0(lVar1);
        if (cVar2 == '\0') {
          cVar2 = FUN_002ba090(lVar1);
          bVar4 = 0;
          bVar3 = 0;
          if (cVar2 != '\0') {
            bVar3 = FUN_002ba0b0(lVar1);
            bVar3 = bVar3 ^ 1;
          }
          cVar2 = FUN_002ba0b0(lVar6);
          if (cVar2 != '\0') {
            bVar4 = FUN_002ba0b0(lVar6);
            bVar4 = bVar4 ^ 1;
          }
          cVar2 = FUN_002ba0b0(param_1);
          if ((bVar3 == 0 && bVar4 == 0) && (cVar2 == '\x01')) {
            cVar2 = FUN_002ba0b0(lVar1);
            bVar4 = 0;
            bVar3 = 0;
            if (cVar2 != '\0') {
              local_1826 = 0;
              local_1610 = 0;
              local_10c = 0;
              local_df = 0;
              local_9f = 0;
              bVar3 = FUN_002ba280(lVar1,local_1830);
              bVar3 = bVar3 ^ 1;
              if (bVar3 == 0) {
                FUN_002b8580(param_1 + 0x1c8,local_1626);
                *(undefined4 *)(param_1 + 0x248) = 0;
              }
            }
            cVar2 = FUN_002ba0b0(lVar6);
            if (cVar2 != '\0') {
              local_3300[0] = 0;
              local_32c0 = 0;
              local_32bb = 0;
              local_327a = 0;
              local_3239 = 0;
              local_31f8 = 0;
              local_31b7 = 0;
              local_3176 = 0;
              local_3135 = 0;
              local_30f4 = 0;
              local_30b3 = 0;
              local_3072 = 0;
              local_3030 = 0;
              local_2ff0 = 0;
              local_2feb = 0;
              local_2faa = 0;
              local_2f69 = 0;
              local_2f28 = 0;
              local_2ee7 = 0;
              local_2ea6 = 0;
              local_2e65 = 0;
              local_2e24 = 0;
              local_2de3 = 0;
              local_2da2 = 0;
              local_2d38 = 0;
              bVar5 = FUN_002bcc70(lVar6,local_3300);
              bVar4 = bVar5 ^ 1;
              if (bVar5 != 0) {
                FUN_002b8580(param_1 + 0x1c8,auStack_2d34 + (long)(local_2d38 + -1) * 0x15);
                *(undefined4 *)(param_1 + 0x248) = 1;
              }
            }
            lVar6 = FUN_000b2020(param_1 + 8);
            bVar5 = lVar6 != 0x4e;
            if (!(bool)bVar5) {
              bVar5 = FUN_002e9b10(param_1 + 0x250,param_1 + 0x234);
              bVar5 = bVar5 ^ 1;
            }
            bVar7 = false;
            if (((bVar3 & 1) == 0) && (bVar4 == 0)) {
              bVar7 = bVar5 == 0;
            }
            *(bool *)(param_1 + 0x27e) = bVar7;
          }
          *(undefined1 *)(param_1 + 0x27d) = 1;
        }
      }
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

