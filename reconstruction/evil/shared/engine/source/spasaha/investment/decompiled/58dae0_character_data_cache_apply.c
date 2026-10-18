
void FUN_0058dae0(long param_1)

{
  long lVar1;
  char cVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  char *pcVar6;
  long lVar7;
  undefined8 uVar8;
  undefined1 local_48 [8];
  undefined4 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_00074a80(local_48,DAT_0273ea80);
  lVar3 = FUN_00074a90(local_48);
  do {
    if (lVar3 == 0) {
      if (*DAT_01a1f100 == local_38) {
        return;
      }
      thunk_FUN_012aa7f6();
      return;
    }
    cVar2 = FUN_0054dd60((long *)(lVar3 + 0x710));
    if (cVar2 != '\0') {
      lVar3 = *(long *)(lVar3 + 0x710);
      if (lVar3 != 0) {
        lVar5 = 0x14;
        lVar4 = param_1;
        do {
          lVar7 = (lVar5 >> 1) * 0xe48;
          lVar1 = *(long *)(lVar4 + 8 + lVar7);
          if (lVar1 <= lVar3) {
            if (lVar3 <= lVar1) {
              lVar3 = (ulong)(uint)((int)((ulong)((lVar4 + lVar7) - param_1) >> 3) * 0x23d9e879) <<
                      0x20;
              if (lVar3 + 0xffffffffU < 0x14ffffffff) {
                lVar3 = (lVar3 >> 0x20) * 0xe48;
                pcVar6 = (char *)(param_1 + lVar3);
                if (pcVar6 != (char *)0x0) {
                  lVar4 = FUN_00587920();
                  uVar8 = 0;
                  if (lVar4 != 0) {
                    uVar8 = *(undefined8 *)(lVar4 + 8);
                  }
                  lVar5 = FUN_00057f80(uVar8);
                  lVar4 = *(long *)(param_1 + 0xe40 + lVar3);
                  if ((*pcVar6 == '\x05') || (lVar4 <= lVar5 && lVar4 != 0)) {
                    FUN_00911850(local_40,param_1 + 0x28 + lVar3,lVar4 <= lVar5 && lVar4 != 0);
                    if (*pcVar6 != '\x06') {
                      *pcVar6 = '\x06';
                    }
                    FUN_0058e2a0();
                  }
                  goto LAB_0058dc48;
                }
              }
              break;
            }
            lVar4 = lVar7 + 0xe48 + lVar4;
            lVar5 = lVar5 + -1;
          }
          lVar5 = lVar5 >> 1;
        } while (lVar5 != 0);
      }
      FUN_00911a70(local_40);
    }
LAB_0058dc48:
    lVar3 = FUN_00074a90(local_48);
  } while( true );
}

