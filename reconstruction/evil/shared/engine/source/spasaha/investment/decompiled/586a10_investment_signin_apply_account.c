
void FUN_00586a10(long param_1,char *param_2)

{
  char *pcVar1;
  undefined *puVar2;
  char cVar3;
  int iVar4;
  long lVar5;
  undefined8 uVar6;
  char *pcVar7;
  long lVar8;
  undefined8 local_90;
  undefined8 local_88;
  undefined8 local_80;
  undefined8 local_78;
  undefined8 local_70;
  undefined8 local_68;
  undefined8 local_60;
  undefined8 local_58;
  undefined8 local_50;
  undefined8 local_48;
  undefined8 local_40;
  undefined8 local_38;
  long local_30;
  
  local_30 = *DAT_01a1f100;
  if (*param_2 == '\x04') {
    *(undefined1 *)(param_1 + 0x41d) = 1;
    goto LAB_00586c04;
  }
  if (*param_2 != '\0') {
    *(undefined1 *)(param_1 + 0x41c) = 1;
    goto LAB_00586c04;
  }
  iVar4 = -1;
  pcVar1 = (char *)(param_1 + -0x30);
  do {
    pcVar7 = pcVar1;
    iVar4 = iVar4 + 1;
    if (0 < iVar4) goto LAB_00586bb7;
    pcVar1 = pcVar7 + 0x30;
  } while (pcVar7[0x30] == '\0');
  if ((pcVar1 != (char *)0x0) && (*pcVar1 == '\x02')) {
    lVar5 = FUN_0058b960();
    if (lVar5 != 0) {
      lVar8 = 0;
      if (*(char *)(lVar5 + 0x38) != '\0') {
        lVar8 = lVar5;
      }
      if (lVar8 != 0) {
        local_40 = *(undefined8 *)(lVar8 + 0x28);
        local_38 = *(undefined8 *)(lVar8 + 0x30);
        local_48 = *(undefined8 *)(lVar8 + 0x20);
        local_50 = *(undefined8 *)(lVar8 + 0x18);
        local_60 = *(undefined8 *)(lVar8 + 8);
        local_58 = *(undefined8 *)(lVar8 + 0x10);
        cVar3 = FUN_002b82d0(&local_60,&stack0x00000008);
        if (cVar3 != '\0') {
          local_78 = *(undefined8 *)(pcVar7 + 0x48);
          local_70 = *(undefined8 *)(pcVar7 + 0x50);
          local_68 = *(undefined8 *)(pcVar7 + 0x58);
          local_88 = *(undefined8 *)(pcVar7 + 0x38);
          local_80 = *(undefined8 *)(param_2 + 8);
          local_90 = CONCAT71((int7)((ulong)*(undefined8 *)pcVar1 >> 8),3);
          iVar4 = thunk_FUN_012aa826(pcVar1,&local_90,0x30);
          if (iVar4 != 0) {
            FUN_002487e0((long)&local_90 + 1);
            *(undefined8 *)(pcVar7 + 0x58) = local_68;
            *(undefined8 *)(pcVar7 + 0x50) = local_70;
            *(undefined8 *)(pcVar7 + 0x48) = local_78;
            *(undefined8 *)(pcVar7 + 0x40) = local_80;
            *(undefined8 *)(pcVar7 + 0x38) = local_88;
            *(undefined8 *)pcVar1 = local_90;
          }
          uVar6 = FUN_00582a40();
          FUN_00580280(uVar6,pcVar7 + 0x31);
          FUN_00586c50();
        }
        goto LAB_00586bb7;
      }
    }
    FUN_002b8260(&local_60);
  }
LAB_00586bb7:
  uVar6 = FUN_0056b260();
  FUN_0056d110(uVar6,param_2 + 0x18);
  *(undefined1 *)(param_1 + 0x48) = 2;
  puVar2 = PTR_DAT_019e4d70;
  local_90 = thunk_FUN_012aac96();
  FUN_00300230(0x31,*(undefined4 *)puVar2,&local_90);
  *(undefined1 *)(param_1 + 0x41e) = 1;
LAB_00586c04:
  if (*DAT_01a1f100 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

