#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from config import engine
from sqlalchemy import inspect
from models import *

def compare_models_with_db():
    """models.py와 실제 데이터베이스 구조를 비교"""
    
    print("🔍 models.py와 실제 데이터베이스 구조 비교 분석")
    print("=" * 60)
    
    # 실제 DB 구조 로드
    with open('database_structure.json', 'r', encoding='utf-8') as f:
        db_structure = json.load(f)
    
    # models.py에서 정의된 테이블들
    model_tables = {
        'users': User,
        'classes': Class,
        'students': Student,
        'subjects': Subject,
        'exams': Exam,
        'grades': Grade,
        'attendance_types': AttendanceType,
        'attendance_reasons': AttendanceReason,
        'attendances': Attendance,
        'monthly_attendances': MonthlyAttendance,
        'yearly_attendances': YearlyAttendance,
        'calendar_events': CalendarEvent
    }
    
    # 실제 DB 테이블들
    db_tables = set(db_structure.keys())
    model_table_names = set(model_tables.keys())
    
    print(f"\n📊 테이블 개수 비교:")
    print(f"  - models.py: {len(model_table_names)}개")
    print(f"  - 실제 DB: {len(db_tables)}개")
    
    # 테이블 존재 여부 확인
    missing_in_db = model_table_names - db_tables
    missing_in_models = db_tables - model_table_names
    
    if missing_in_db:
        print(f"\n❌ models.py에만 있는 테이블 (DB에 없음):")
        for table in missing_in_db:
            print(f"  - {table}")
    
    if missing_in_models:
        print(f"\n❌ DB에만 있는 테이블 (models.py에 없음):")
        for table in missing_in_models:
            print(f"  - {table}")
    
    if not missing_in_db and not missing_in_models:
        print(f"\n✅ 모든 테이블이 일치합니다!")
    
    # 각 테이블의 컬럼 비교
    print(f"\n🔍 컬럼 구조 비교:")
    
    differences_found = False
    
    for table_name in model_table_names & db_tables:
        print(f"\n--- {table_name} 테이블 ---")
        
        # models.py의 컬럼 정보
        model_columns = {}
        model_table = model_tables[table_name]
        
        for column in model_table.__table__.columns:
            model_columns[column.name] = {
                'type': str(column.type),
                'nullable': column.nullable,
                'primary_key': column.primary_key,
                'default': column.default
            }
        
        # 실제 DB의 컬럼 정보
        db_columns = {}
        for col in db_structure[table_name]['columns']:
            db_columns[col['name']] = {
                'type': col['type'],
                'nullable': col['nullable'],
                'primary_key': col['primary_key'],
                'default': col['default']
            }
        
        # 컬럼 비교
        model_col_names = set(model_columns.keys())
        db_col_names = set(db_columns.keys())
        
        missing_in_db_cols = model_col_names - db_col_names
        missing_in_models_cols = db_col_names - model_col_names
        
        if missing_in_db_cols:
            print(f"  ❌ models.py에만 있는 컬럼: {list(missing_in_db_cols)}")
            differences_found = True
        
        if missing_in_models_cols:
            print(f"  ❌ DB에만 있는 컬럼: {list(missing_in_models_cols)}")
            differences_found = True
        
        # 공통 컬럼들의 타입/속성 비교
        common_cols = model_col_names & db_col_names
        for col_name in common_cols:
            model_col = model_columns[col_name]
            db_col = db_columns[col_name]
            
            # 타입 비교 (간단한 비교)
            model_type = model_col['type'].upper()
            db_type = db_col['type'].upper()
            
            if model_type != db_type:
                print(f"  ⚠️  컬럼 '{col_name}' 타입 불일치:")
                print(f"     models.py: {model_type}")
                print(f"     실제 DB: {db_type}")
                differences_found = True
            
            # nullable 비교
            if model_col['nullable'] != db_col['nullable']:
                print(f"  ⚠️  컬럼 '{col_name}' nullable 불일치:")
                print(f"     models.py: {model_col['nullable']}")
                print(f"     실제 DB: {db_col['nullable']}")
                differences_found = True
        
        if not missing_in_db_cols and not missing_in_models_cols:
            print(f"  ✅ 컬럼 구조 일치")
    
    # 주요 차이점 요약
    print(f"\n📋 주요 차이점 요약:")
    
    if not differences_found:
        print("  ✅ models.py와 실제 DB 구조가 완전히 일치합니다!")
    else:
        print("  ⚠️  일부 차이점이 발견되었습니다.")
        print("  💡 권장사항:")
        print("    1. DB 마이그레이션을 통해 구조를 동기화하세요")
        print("    2. 또는 models.py를 실제 DB 구조에 맞게 수정하세요")
    
    return differences_found

if __name__ == "__main__":
    try:
        has_differences = compare_models_with_db()
        if has_differences:
            print(f"\n❌ 구조 불일치 발견!")
        else:
            print(f"\n✅ 구조 일치 확인!")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc() 