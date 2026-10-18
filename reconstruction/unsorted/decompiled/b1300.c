
long FUN_000b1300(long param_1,long param_2,undefined8 param_3,uint param_4,int param_5)

{
  long lVar1;
  uint uVar2;
  long lVar3;
  ulong uVar4;
  long *plVar5;
  long lVar6;
  uint *puVar7;
  long lVar8;
  ulong uVar9;
  uint *puVar10;
  
  lVar8 = DAT_01ad4f48;
  lVar3 = 0x20;
  if (*(char *)(param_1 + 0xc4) != '\0') {
    lVar3 = 0x40;
  }
  uVar9 = param_2 + 0xf + lVar3 & 0xfffffffffffffff0;
  lVar3 = *(long *)(param_1 + 0x30);
  lVar1 = *(long *)(param_1 + 0x88);
  if (lVar1 == DAT_01ad4f48) {
    puVar10 = (uint *)(lVar3 + 0x10);
  }
  else {
    puVar10 = (uint *)(((ulong)*(uint *)(lVar3 + lVar1) & 0xfffffff) + lVar3 + lVar1);
  }
  if ((long)puVar10 + uVar9 <=
      (ulong)((*(long *)(param_1 + 0x50) + lVar3) - *(long *)(param_1 + 0xb8))) {
    FUN_000b0f60(param_1,lVar1,DAT_01ad4f48,puVar10,uVar9);
    if (puVar10 != (uint *)0x0) goto LAB_000b15f4;
    lVar3 = *(long *)(param_1 + 0x30);
  }
  lVar1 = *(long *)(param_1 + 0x80);
  if (lVar1 == DAT_01ad4f48) {
    uVar4 = (*(long *)(param_1 + 0x50) + lVar3) - *(long *)(param_1 + 0xb8);
  }
  else {
    uVar4 = lVar3 + lVar1;
  }
  if (uVar4 < lVar3 + 0x10 + uVar9) {
LAB_000b140e:
    if (*(long *)(param_1 + 0x98) == 0) {
      plVar5 = (long *)(param_1 + 0x80);
    }
    else {
      plVar5 = (long *)(param_1 + 0x98);
    }
    if (*plVar5 == DAT_01ad4f48) {
      puVar10 = (uint *)0x0;
LAB_000b148c:
      if (*(char *)(param_1 + 0xc5) != '\0') {
        FUN_000b00c0(param_1);
        lVar3 = *(long *)(param_1 + 0x30);
        lVar1 = *(long *)(param_1 + 0x88);
        if (lVar1 == DAT_01ad4f48) {
          puVar7 = (uint *)(lVar3 + 0x10);
        }
        else {
          puVar7 = (uint *)(((ulong)*(uint *)(lVar3 + lVar1) & 0xfffffff) + lVar3 + lVar1);
        }
        puVar10 = (uint *)0x0;
        if ((long)puVar7 + uVar9 <=
            (ulong)((lVar3 + *(long *)(param_1 + 0x50)) - *(long *)(param_1 + 0xb8))) {
          FUN_000b0f60(param_1,lVar1,DAT_01ad4f48,puVar7,uVar9);
          puVar10 = puVar7;
        }
      }
    }
    else {
      lVar3 = *(long *)(param_1 + 0x30);
      lVar1 = *plVar5;
      do {
        lVar6 = lVar1;
        lVar1 = *(long *)(lVar6 + 0x10 + lVar3);
        if (lVar1 == DAT_01ad4f48) {
          puVar10 = (uint *)0x0;
          goto LAB_000b148c;
        }
        puVar10 = (uint *)(((ulong)*(uint *)(lVar6 + lVar3) & 0xfffffff) + lVar6 + lVar3);
      } while ((ulong)(lVar1 + lVar3) < (long)puVar10 + uVar9);
      FUN_000b0f60(param_1,lVar6,lVar1,puVar10,uVar9);
      if (puVar10 == (uint *)0x0) goto LAB_000b148c;
    }
    if (puVar10 != (uint *)0x0) goto LAB_000b15f4;
    if (*(char *)(param_1 + 199) == '\0') {
      return lVar8;
    }
    uVar4 = param_2 + 0xffffU & 0xffffffffffff0000;
    if (((long)uVar4 <=
         (*(long *)(param_1 + 0xf8) - *(long *)(param_1 + 0xe8)) - *(long *)(param_1 + 0xf0)) &&
       (lVar3 = FUN_000b4630(param_1 + 0xe8,uVar4,0), lVar3 != 0)) {
      lVar3 = uVar4 + *(long *)(param_1 + 0x50);
      *(long *)(param_1 + 0x50) = lVar3;
      if (*(code **)(param_1 + 0xd8) != (code *)0x0) {
        (**(code **)(param_1 + 0xd8))(*(undefined8 *)(param_1 + 0x30),lVar3);
      }
    }
    lVar3 = *(long *)(param_1 + 0x30);
    lVar1 = *(long *)(param_1 + 0x88);
    if (lVar1 == DAT_01ad4f48) {
      puVar10 = (uint *)(lVar3 + 0x10);
    }
    else {
      puVar10 = (uint *)(((ulong)*(uint *)(lVar3 + lVar1) & 0xfffffff) + lVar3 + lVar1);
    }
    if ((ulong)((lVar3 + *(long *)(param_1 + 0x50)) - *(long *)(param_1 + 0xb8)) <
        (long)puVar10 + uVar9) {
      return lVar8;
    }
    FUN_000b0f60(param_1,lVar1,DAT_01ad4f48,puVar10,uVar9);
  }
  else {
    puVar10 = (uint *)(lVar3 + 0x10);
    FUN_000b0f60(param_1,DAT_01ad4f48,lVar1,puVar10,uVar9);
    if (puVar10 == (uint *)0x0) goto LAB_000b140e;
  }
  if (puVar10 == (uint *)0x0) {
    return lVar8;
  }
LAB_000b15f4:
  lVar8 = 0x20;
  if (*(char *)(param_1 + 0xc4) != '\0') {
    lVar8 = 0x40;
  }
  if (*(code **)(param_1 + 200) != (code *)0x0) {
    (**(code **)(param_1 + 200))(puVar10,lVar8);
  }
  puVar10[1] = param_4;
  lVar3 = ((ulong)*puVar10 & 0xfffffff) + *(long *)(param_1 + 0x58);
  *(long *)(param_1 + 0x58) = lVar3;
  if (*(long *)(param_1 + 0x50) - *(long *)(param_1 + 0xb8) < lVar3) {
    if (DAT_01a231f0 == (code *)0x0) {
      FUN_0005c750(s_tag_heap_used_size_overflow_in_a_016137e5);
      s__libexec_ld_elf_so_1_00000000[1] = '*';
      s__libexec_ld_elf_so_1_00000000[2] = '\0';
      s__libexec_ld_elf_so_1_00000000[3] = '\0';
      s__libexec_ld_elf_so_1_00000000[4] = '\0';
    }
    else {
      (*DAT_01a231f0)(0,s_tag_heap_used_size_overflow_in_a_016137e5);
    }
  }
  lVar3 = *(long *)(param_1 + 0x60);
  if (*(long *)(param_1 + 0x60) <= *(long *)(param_1 + 0x58)) {
    lVar3 = *(long *)(param_1 + 0x58);
  }
  *(long *)(param_1 + 0x60) = lVar3;
  if (*(char *)(param_1 + 0xc4) != '\0') {
    puVar10[8] = 0;
    puVar10[9] = 0;
    puVar10[10] = 0;
    puVar10[0xb] = 0;
    puVar10[0xc] = param_5 << 0x18;
    uVar2 = FUN_000697a0();
    puVar10[0xd] = uVar2;
  }
  if (*(code **)(param_1 + 0xd0) != (code *)0x0) {
    (**(code **)(param_1 + 0xd0))(puVar10,lVar8);
  }
  return (long)puVar10 + (lVar8 - *(long *)(param_1 + 0x30));
}

