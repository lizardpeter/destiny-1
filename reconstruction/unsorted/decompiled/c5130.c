
void FUN_000c5130(void)

{
  bool bVar1;
  long lVar2;
  uint uVar3;
  uint uVar4;
  char cVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  long lVar9;
  char *pcVar10;
  char *pcVar11;
  undefined **ppuVar12;
  uint uVar13;
  undefined1 local_2d8 [4];
  undefined4 local_2d4;
  char local_1b9 [321];
  undefined1 local_78 [64];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_0008a8c0(local_2d8,2,s_crs_test_txt_016159f7);
  cVar5 = FUN_0008ab90(local_2d8);
  if (cVar5 != '\0') {
    cVar5 = FUN_0008ac30(local_2d8,2,local_2d4);
    if (cVar5 == '\0') {
      FUN_000c58c0(s_crs_test__Test_file_exist_but_ca_0161573f);
    }
    else {
      cVar5 = FUN_0008bf90(local_2d8,0x140,local_1b9 + 1);
      if (cVar5 == '\0') {
        bVar1 = false;
        FUN_000c58c0(s_crs_test__CRS_Test_String_missin_0161557c);
      }
      else {
        iVar6 = FUN_00065290(local_1b9 + 1,0x140);
        lVar2 = 0;
        do {
          lVar9 = lVar2;
          iVar7 = (int)lVar9;
          if (iVar6 <= iVar7) break;
          cVar5 = FUN_00064df0((int)local_1b9[lVar9 + 1]);
          lVar2 = lVar9 + 1;
        } while (cVar5 != '\0');
        if (0 < iVar7) {
          thunk_FUN_012aaab6(local_1b9 + 1,local_1b9 + lVar9 + 1,(long)(iVar6 - iVar7));
          local_1b9[(long)(iVar6 - iVar7) + 1] = '\0';
        }
        iVar6 = FUN_00065290(local_1b9 + 1,0x140);
        ppuVar12 = &PTR_DAT_01905d70;
        uVar3 = 0;
        if (0 < iVar6) {
          pcVar10 = local_1b9 + 1 + (long)iVar6 + -1;
          do {
            cVar5 = FUN_00064df0((int)*pcVar10);
            uVar3 = 0;
            if (cVar5 == '\0') break;
            *pcVar10 = '\0';
            pcVar10 = pcVar10 + -1;
            iVar6 = iVar6 + -1;
          } while (0 < iVar6);
        }
        do {
          uVar13 = uVar3;
          uVar4 = DAT_01b2f870;
          if (0xb < (int)uVar13) break;
          iVar6 = thunk_FUN_012aab16(local_1b9 + 1,*ppuVar12,0x140);
          ppuVar12 = ppuVar12 + 1;
          uVar3 = uVar13 + 1;
          uVar4 = uVar13;
        } while (iVar6 != 0);
        DAT_01b2f870 = uVar4;
        bVar1 = true;
        if (DAT_01b2f870 == 0) {
          bVar1 = false;
          FUN_000c58c0(s_crs_test__Unknown_CRS_Test_Strin_01615555,local_1b9 + 1);
        }
      }
      cVar5 = FUN_0008bf90(local_2d8,0x140,local_1b9 + 1);
      if (cVar5 == '\0') {
        bVar1 = false;
        FUN_000c58c0(s_crs_test__CRS_Test_Game_State_St_016155d1);
      }
      else {
        iVar6 = FUN_00065290(local_1b9 + 1,0x140);
        lVar2 = 0;
        do {
          lVar9 = lVar2;
          iVar7 = (int)lVar9;
          if (iVar6 <= iVar7) break;
          cVar5 = FUN_00064df0((int)local_1b9[lVar9 + 1]);
          lVar2 = lVar9 + 1;
        } while (cVar5 != '\0');
        if (0 < iVar7) {
          thunk_FUN_012aaab6(local_1b9 + 1,local_1b9 + lVar9 + 1,(long)(iVar6 - iVar7));
          local_1b9[(long)(iVar6 - iVar7) + 1] = '\0';
        }
        iVar6 = FUN_00065290(local_1b9 + 1,0x140);
        ppuVar12 = &PTR_DAT_01905dd0;
        uVar3 = 0;
        if (0 < iVar6) {
          pcVar10 = local_1b9 + 1 + (long)iVar6 + -1;
          do {
            cVar5 = FUN_00064df0((int)*pcVar10);
            uVar3 = 0;
            if (cVar5 == '\0') break;
            *pcVar10 = '\0';
            pcVar10 = pcVar10 + -1;
            iVar6 = iVar6 + -1;
          } while (0 < iVar6);
        }
        do {
          uVar13 = uVar3;
          uVar4 = DAT_01b2f874;
          if (3 < (int)uVar13) break;
          iVar6 = thunk_FUN_012aab16(local_1b9 + 1,*ppuVar12,0x140);
          ppuVar12 = ppuVar12 + 1;
          uVar3 = uVar13 + 1;
          uVar4 = uVar13;
        } while (iVar6 != 0);
        DAT_01b2f874 = uVar4;
        if (DAT_01b2f874 == 0) {
          bVar1 = false;
          FUN_000c58c0(s_crs_test__Unknown_CRS_Test_Game_S_0161559f,local_1b9 + 1);
        }
      }
      cVar5 = FUN_0008bf90(local_2d8,0x140,local_1b9 + 1);
      if (cVar5 != '\0') {
        pcVar10 = local_1b9 + 1;
        do {
          iVar6 = FUN_00065290(pcVar10,0x140);
          lVar2 = 0;
          do {
            lVar9 = lVar2;
            iVar7 = (int)lVar9;
            if (iVar6 <= iVar7) break;
            cVar5 = FUN_00064df0((int)local_1b9[lVar9 + 1]);
            lVar2 = lVar9 + 1;
          } while (cVar5 != '\0');
          if (0 < iVar7) {
            thunk_FUN_012aaab6(pcVar10,local_1b9 + lVar9 + 1,(long)(iVar6 - iVar7));
            local_1b9[(long)(iVar6 - iVar7) + 1] = '\0';
          }
          iVar6 = FUN_00065290(pcVar10,0x140);
          if (0 < iVar6) {
            pcVar11 = local_1b9 + iVar6;
            do {
              cVar5 = FUN_00064df0((int)*pcVar11);
              if (cVar5 == '\0') break;
              *pcVar11 = '\0';
              pcVar11 = pcVar11 + -1;
              iVar6 = iVar6 + -1;
            } while (0 < iVar6);
          }
          iVar6 = FUN_00065290(s_double_tap_01615913,0x140);
          iVar6 = thunk_FUN_012aab16(s_double_tap_01615913,pcVar10,(long)iVar6);
          if (iVar6 == 0) {
            iVar6 = thunk_FUN_012aa816(s_double_tap_01615913);
            pcVar11 = &DAT_012ad038;
            if (-1 < iVar6) {
              iVar7 = FUN_00065290(pcVar10,0x140);
              pcVar11 = &DAT_012ad038;
              if (iVar6 <= iVar7) {
                pcVar11 = local_1b9 + (long)iVar6 + 1;
              }
            }
            FUN_00065030(local_78,pcVar11,0x40);
            ppuVar12 = &PTR_DAT_01905d70;
            iVar7 = 0;
            do {
              iVar6 = iVar7;
              if (0xb < iVar6) goto LAB_000c56b0;
              iVar8 = FUN_00064f00(local_78,*ppuVar12,0x40);
              ppuVar12 = ppuVar12 + 1;
              iVar7 = iVar6 + 1;
            } while (iVar8 != 0);
LAB_000c56a0:
            DAT_01b2f890 = iVar6;
            pcVar11 = s_crs_test__Applying_additional_se_016155ff;
          }
          else {
            iVar6 = thunk_FUN_012aab16(pcVar10,s_saved_film_record_01615931,0x140);
            if (iVar6 == 0) {
              DAT_01b2f888 = 1;
              iVar6 = DAT_01b2f890;
              goto LAB_000c56a0;
            }
            iVar6 = thunk_FUN_012aab16(pcVar10,s_saved_film_play_last_01615943,0x140);
            if (iVar6 == 0) {
              DAT_01b2f888 = 2;
              iVar6 = DAT_01b2f890;
              goto LAB_000c56a0;
            }
            iVar6 = thunk_FUN_012aab16(pcVar10,s_no_dump_01615958,0x140);
            if (iVar6 == 0) {
              DAT_01b2f88d = 1;
              iVar6 = DAT_01b2f890;
              goto LAB_000c56a0;
            }
            iVar6 = FUN_00065290(s_ticketdbg_folder_0161591f,0x140);
            iVar7 = thunk_FUN_012aab16(s_ticketdbg_folder_0161591f,pcVar10,(long)iVar6);
            iVar6 = DAT_01b2f890;
            if (iVar7 == 0) goto LAB_000c56a0;
LAB_000c56b0:
            bVar1 = false;
            pcVar11 = s_crs_test__Unknown_additional_set_01615631;
          }
          FUN_000c58c0(pcVar11,pcVar10);
          cVar5 = FUN_0008bf90(local_2d8,0x140,pcVar10);
        } while (cVar5 != '\0');
      }
      if (((bVar1) && (DAT_01b2f870 != 0)) && (DAT_01b2f874 != 0)) {
        FUN_000c58c0(s_crs_test_________________________01615662);
        FUN_000c58c0(s_crs_test__Running_CRS_Test___s__a_0161569a,(&PTR_DAT_01905d70)[DAT_01b2f870],
                     (&PTR_DAT_01905dd0)[DAT_01b2f874]);
      }
      else {
        DAT_01b2f870 = 0;
        DAT_01b2f874 = 0;
        FUN_000c58c0(s_crs_test_________________________01615662);
        FUN_000c58c0(s_crs_test__Failed_to_load_CRS_Tes_016156f8);
        FUN_000c58c0(s_crs_test___s_contents__0161571b,s_crs_test_txt_016159f7);
        FUN_0008b5b0(local_2d8,0);
        cVar5 = FUN_0008bf90(local_2d8,0x140,local_1b9 + 1);
        if (cVar5 != '\0') {
          pcVar10 = local_1b9 + 1;
          do {
            iVar6 = FUN_00065290(pcVar10,0x140);
            if (0 < iVar6) {
              pcVar11 = local_1b9 + iVar6;
              do {
                if (*pcVar11 != '\n') break;
                *pcVar11 = '\0';
                pcVar11 = pcVar11 + -1;
                iVar6 = iVar6 + -1;
              } while (0 < iVar6);
            }
            iVar6 = FUN_00065290(pcVar10,0x140);
            if (0 < iVar6) {
              pcVar11 = local_1b9 + iVar6;
              do {
                if (*pcVar11 != '\r') break;
                *pcVar11 = '\0';
                pcVar11 = pcVar11 + -1;
                iVar6 = iVar6 + -1;
              } while (0 < iVar6);
            }
            FUN_000c58c0(s_crs_test___s_01615732,pcVar10);
            cVar5 = FUN_0008bf90(local_2d8,0x140,pcVar10);
          } while (cVar5 != '\0');
        }
      }
      FUN_000c58c0(s_crs_test_________________________016156c2);
      FUN_0008aa70(local_2d8);
    }
  }
  thunk_FUN_0008aa70(local_2d8);
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

