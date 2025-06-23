import streamlit as st
import pandas as pd
from datetime import datetime
import os
import plotly.express as px

class AttendanceSystem:
    def __init__(self):
        self.data_file = 'attendance_data.xlsx'
        self.members_file = 'members_list.txt'
        self.departments = ['락킹', '왁킹', '힙합', '걸스힙합', '하우스', '브레이킹']
        self.initialize_data_file()
        self.initialize_members_file()

    def initialize_data_file(self):
        if not os.path.exists(self.data_file):
            df = pd.DataFrame(columns=['날짜', '이름', '부서', '출석상태', '비고'])
            df.to_excel(self.data_file, index=False)

    def initialize_members_file(self):
        if not os.path.exists(self.members_file):
            with open(self.members_file, 'w', encoding='utf-8') as f:
                f.write("")

    def get_members_list(self):
        try:
            with open(self.members_file, 'r', encoding='utf-8') as f:
                members = {}
                for line in f:
                    if line.strip():
                        name, dept = line.strip().split(',')
                        members[name.strip()] = dept.strip()
            return members
        except FileNotFoundError:
            return {}

    def add_member(self, name, department):
        if department not in self.departments:
            return False, "존재하지 않는 부서입니다."
            
        members = self.get_members_list()
        if name not in members:
            with open(self.members_file, 'a', encoding='utf-8') as f:
                f.write(f"{name},{department}\n")
            return True, f"{name}님이 {department} 부서에 추가되었습니다."
        return False, f"{name}님은 이미 동아리원 목록에 있습니다."

    def remove_member(self, name):
        members = self.get_members_list()
        if name in members:
            del members[name]
            with open(self.members_file, 'w', encoding='utf-8') as f:
                for name, dept in members.items():
                    f.write(f"{name},{dept}\n")
            return True
        return False

    def check_attendance(self, names, status='출석', date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        df = pd.read_excel(self.data_file)
        
        name_list = [name.strip() for name in names.replace(',', ' ').split() if name.strip()]
        
        if not name_list:
            return "입력된 이름이 없습니다."
        
        valid_members = self.get_members_list()
        results = []
        invalid_names = []
        
        for name in name_list:
            if name not in valid_members:
                invalid_names.append(name)
        
        if invalid_names:
            return f"다음 이름은 동아리원 목록에 없습니다: {', '.join(invalid_names)}"
        
        for name in name_list:
            if len(df[(df['날짜'] == date) & (df['이름'] == name)]) > 0:
                results.append(f"{name}님은 이미 {date} 출석 기록이 있습니다.")
                continue
            
            new_record = pd.DataFrame({
                '날짜': [date],
                '이름': [name],
                '부서': [valid_members[name]],
                '출석상태': [status],
                '비고': ['']
            })
            
            df = pd.concat([df, new_record], ignore_index=True)
            results.append(f"{name}님의 출석이 기록되었습니다. (날짜: {date}, 상태: {status})")
        
        df.to_excel(self.data_file, index=False)
        return "\n".join(results)

    def get_attendance_summary(self, name=None, department=None):
        df = pd.read_excel(self.data_file)
        members = self.get_members_list()
        
        if name:
            if name not in members:
                return None, f"{name}님은 동아리원 목록에 없습니다."
            df = df[df['이름'] == name]
        elif department:
            if department not in self.departments:
                return None, f"존재하지 않는 부서입니다."
            df = df[df['부서'] == department]
        
        if len(df) == 0:
            return None, "출석 기록이 없습니다."
        
        if name:
            total_days = len(df)
            attendance_count = len(df[df['출석상태'] == '출석'])
            late_count = len(df[df['출석상태'] == '지각'])
            absent_count = len(df[df['출석상태'] == '결석'])
            
            attendance_rate = (attendance_count / total_days) * 100 if total_days > 0 else 0
            
            summary = {
                '이름': name,
                '부서': members[name],
                '총_활동일수': total_days,
                '출석': attendance_count,
                '지각': late_count,
                '결석': absent_count,
                '출석률': attendance_rate
            }
            
            return summary, None
        else:
            summary = []
            for dept_member in [m for m, d in members.items() if d == department]:
                member_df = df[df['이름'] == dept_member]
                if len(member_df) > 0:
                    total_days = len(member_df)
                    attendance_count = len(member_df[member_df['출석상태'] == '출석'])
                    late_count = len(member_df[member_df['출석상태'] == '지각'])
                    absent_count = len(member_df[member_df['출석상태'] == '결석'])
                    attendance_rate = (attendance_count / total_days) * 100 if total_days > 0 else 0
                    
                    summary.append({
                        '이름': dept_member,
                        '출석': attendance_count,
                        '지각': late_count,
                        '결석': absent_count,
                        '출석률': attendance_rate
                    })
            
            return summary, None

    def get_total_statistics(self):
        df = pd.read_excel(self.data_file)
        members = self.get_members_list()
        
        if len(df) == 0:
            return None, "출석 기록이 없습니다."
        
        # 전체 통계
        total_attendance = len(df[df['출석상태'] == '출석'])
        total_late = len(df[df['출석상태'] == '지각'])
        total_absent = len(df[df['출석상태'] == '결석'])
        
        # 부서별 통계
        dept_stats = {}
        for dept in self.departments:
            dept_df = df[df['부서'] == dept]
            dept_stats[dept] = {
                '출석': len(dept_df[dept_df['출석상태'] == '출석']),
                '지각': len(dept_df[dept_df['출석상태'] == '지각']),
                '결석': len(dept_df[dept_df['출석상태'] == '결석'])
            }
        
        # 날짜별 통계
        date_stats = df.groupby('날짜')['출석상태'].value_counts().unstack(fill_value=0)
        
        return {
            '전체': {
                '출석': total_attendance,
                '지각': total_late,
                '결석': total_absent
            },
            '부서별': dept_stats,
            '날짜별': date_stats
        }, None

    def view_attendance(self, date=None):
        df = pd.read_excel(self.data_file)
        
        if date:
            df = df[df['날짜'] == date]
            
        return df

    def get_practice_count(self, start_date=None, end_date=None):
        df = pd.read_excel(self.data_file)
        
        if start_date and end_date:
            df = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)]
        
        # 날짜별 출석 인원 수 계산
        daily_count = df.groupby('날짜').size().reset_index(name='출석인원')
        
        # 부서별 출석 인원 수 계산
        dept_count = df.groupby(['날짜', '부서']).size().reset_index(name='출석인원')
        
        return daily_count, dept_count

    def modify_attendance(self, date, name, new_status):
        df = pd.read_excel(self.data_file)
        
        # 해당 날짜와 이름에 해당하는 기록 찾기
        mask = (df['날짜'] == date) & (df['이름'] == name)
        if not any(mask):
            return False, f"{date}에 {name}님의 출석 기록이 없습니다."
        
        # 출석 상태 수정
        df.loc[mask, '출석상태'] = new_status
        df.to_excel(self.data_file, index=False)
        return True, f"{name}님의 {date} 출석 상태가 {new_status}로 수정되었습니다."

    def get_summary_until_date(self, until_date, department=None):
        df = pd.read_excel(self.data_file)
        members = self.get_members_list()
        
        # 날짜 필터링
        df = df[df['날짜'] <= until_date]
        
        if department:
            df = df[df['부서'] == department]
            filtered_members = [m for m, d in members.items() if d == department]
        else:
            filtered_members = list(members.keys())
        
        summary = []
        for name in filtered_members:
            member_df = df[df['이름'] == name]
            if len(member_df) > 0:
                attendance_count = len(member_df[member_df['출석상태'] == '출석'])
                late_count = len(member_df[member_df['출석상태'] == '지각'])
                absent_count = len(member_df[member_df['출석상태'] == '결석'])
                summary.append({
                    '이름': name,
                    '부서': members[name],
                    '출석': attendance_count,
                    '지각': late_count,
                    '결석': absent_count
                })
        return summary

def main():
    st.set_page_config(page_title="동아리 출결 관리 시스템", layout="wide")
    
    st.title("동아리 출결 관리 시스템")
    
    system = AttendanceSystem()
    
    # 사이드바 메뉴
    menu = st.sidebar.selectbox(
        "메뉴 선택",
        ["출석 체크", "출석 현황 조회", "날짜별 출석 조회", "연습 진행 현황", "동아리원 관리", "출석 기록 수정"]
    )
    
    if menu == "출석 체크":
        st.header("출석 체크")
        
        # 날짜 선택
        selected_date = st.date_input(
            "출석 날짜를 선택하세요",
            value=datetime.now(),
            format="YYYY-MM-DD"
        )
        
        # 이름 입력
        names = st.text_input("이름을 입력하세요 (쉼표나 공백으로 구분)", 
                            help="예시: 홍길동, 김철수 이영희")
        
        # 출석 상태 선택
        status = st.radio("출석 상태를 선택하세요", ["출석", "지각", "결석"])
        
        if st.button("출석 체크"):
            if names:
                result = system.check_attendance(
                    names, 
                    status, 
                    selected_date.strftime('%Y-%m-%d')
                )
                st.write(result)
            else:
                st.warning("이름을 입력해주세요.")
    
    elif menu == "출석 현황 조회":
        st.header("출석 현황 조회")
        
        # 조회 방식 선택
        view_type = st.radio("조회 방식을 선택하세요", ["전체 통계", "개인별 조회", "부서별 조회", "최종 연습 일자별 통계"])
        
        if view_type == "전체 통계":
            if st.button("통계 조회"):
                stats, error = system.get_total_statistics()
                if error:
                    st.error(error)
                else:
                    # 전체 통계
                    st.subheader("전체 출석 통계")
                    total_stats = stats['전체']
                    
                    # 전체 통계 차트
                    total_data = {
                        '상태': ['출석', '지각', '결석'],
                        '횟수': [total_stats['출석'], total_stats['지각'], total_stats['결석']]
                    }
                    df_total = pd.DataFrame(total_data)
                    fig = px.pie(df_total, values='횟수', names='상태', 
                               title='전체 출석 현황')
                    st.plotly_chart(fig)
                    
                    # 부서별 통계
                    st.subheader("부서별 출석 통계")
                    dept_stats = stats['부서별']
                    
                    # 부서별 통계 테이블
                    dept_data = []
                    for dept, stat in dept_stats.items():
                        dept_data.append({
                            '부서': dept,
                            '출석': stat['출석'],
                            '지각': stat['지각'],
                            '결석': stat['결석']
                        })
                    df_dept = pd.DataFrame(dept_data)
                    st.dataframe(df_dept)
                    
                    # 부서별 통계 차트
                    fig = px.bar(df_dept, x='부서', y=['출석', '지각', '결석'],
                               title='부서별 출석 현황',
                               barmode='group')
                    st.plotly_chart(fig)
                    
                    # 날짜별 통계
                    st.subheader("날짜별 출석 통계")
                    date_stats = stats['날짜별']
                    st.dataframe(date_stats)
                    
                    # 날짜별 통계 차트
                    fig = px.line(date_stats, title='날짜별 출석 현황')
                    st.plotly_chart(fig)
        
        elif view_type == "개인별 조회":
            name = st.text_input("조회할 이름을 입력하세요")
            if st.button("조회"):
                if name:
                    summary, error = system.get_attendance_summary(name=name)
                    if error:
                        st.error(error)
                    else:
                        st.subheader(f"{summary['이름']}님의 출석 현황")
                        st.write(f"부서: {summary['부서']}")
                        st.write(f"총 활동일수: {summary['총_활동일수']}일")
                        
                        # 출석 현황 차트
                        attendance_data = {
                            '상태': ['출석', '지각', '결석'],
                            '횟수': [summary['출석'], summary['지각'], summary['결석']]
                        }
                        df = pd.DataFrame(attendance_data)
                        fig = px.pie(df, values='횟수', names='상태', title='출석 현황')
                        st.plotly_chart(fig)
                        
                        st.write(f"출석률: {summary['출석률']:.1f}%")
                else:
                    st.warning("이름을 입력해주세요.")
        
        elif view_type == "부서별 조회":
            department = st.selectbox("부서를 선택하세요", system.departments)
            if st.button("조회"):
                summary, error = system.get_attendance_summary(department=department)
                if error:
                    st.error(error)
                else:
                    st.subheader(f"{department} 부서 출석 현황")
                    
                    # 부서별 출석 현황 테이블
                    df = pd.DataFrame(summary)
                    st.dataframe(df)
                    
                    # 부서별 출석률 차트
                    fig = px.bar(df, x='이름', y='출석률', 
                               title=f'{department} 부서 출석률')
                    st.plotly_chart(fig)
        
        elif view_type == "최종 연습 일자별 통계":
            until_date = st.date_input("최종 연습 일자를 선택하세요", value=datetime.now(), format="YYYY-MM-DD")
            dept_option = st.selectbox("부서(전체는 선택 안함)", ["전체"] + system.departments)
            if st.button("통계 조회"):
                if dept_option == "전체":
                    summary = system.get_summary_until_date(until_date.strftime('%Y-%m-%d'))
                else:
                    summary = system.get_summary_until_date(until_date.strftime('%Y-%m-%d'), department=dept_option)
                if summary:
                    df = pd.DataFrame(summary)
                    st.dataframe(df)
                    fig = px.bar(df, x='이름', y=['출석', '지각', '결석'], barmode='group', title='최종 연습 일자별 출석 통계')
                    st.plotly_chart(fig)
                else:
                    st.info("해당 기간에 출석 기록이 없습니다.")
    
    elif menu == "날짜별 출석 조회":
        st.header("날짜별 출석 조회")
        
        date = st.date_input("조회할 날짜를 선택하세요")
        if st.button("조회"):
            df = system.view_attendance(date.strftime('%Y-%m-%d'))
            if len(df) > 0:
                st.dataframe(df)
                
                # 부서별 출석 현황
                st.subheader("부서별 출석 현황")
                dept_summary = df.groupby('부서').size().reset_index(name='출석인원')
                fig = px.pie(dept_summary, values='출석인원', names='부서', 
                           title='부서별 출석 인원')
                st.plotly_chart(fig)
            else:
                st.info("해당 날짜의 출석 기록이 없습니다.")
    
    elif menu == "연습 진행 현황":
        st.header("연습 진행 현황")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("시작 날짜")
        with col2:
            end_date = st.date_input("종료 날짜")
        
        if st.button("조회"):
            daily_count, dept_count = system.get_practice_count(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            if len(daily_count) > 0:
                # 전체 출석 인원 추이
                st.subheader("전체 출석 인원 추이")
                fig = px.line(daily_count, x='날짜', y='출석인원',
                            title='날짜별 출석 인원 추이')
                st.plotly_chart(fig)
                
                # 부서별 출석 인원 추이
                st.subheader("부서별 출석 인원 추이")
                fig = px.line(dept_count, x='날짜', y='출석인원', color='부서',
                            title='부서별 출석 인원 추이')
                st.plotly_chart(fig)
                
                # 통계 정보
                st.subheader("통계 정보")
                total_practices = len(daily_count)
                total_attendance = daily_count['출석인원'].sum()
                avg_attendance = total_attendance / total_practices if total_practices > 0 else 0
                
                st.write(f"총 연습 횟수: {total_practices}회")
                st.write(f"총 출석 인원: {total_attendance}명")
                st.write(f"평균 출석 인원: {avg_attendance:.1f}명")
            else:
                st.info("선택한 기간의 출석 기록이 없습니다.")
    
    elif menu == "동아리원 관리":
        st.header("동아리원 관리")
        
        submenu = st.radio("관리 메뉴 선택", ["동아리원 목록", "동아리원 추가", "동아리원 삭제"])
        
        if submenu == "동아리원 목록":
            members = system.get_members_list()
            if members:
                for dept in system.departments:
                    st.subheader(f"[{dept}]")
                    dept_members = [name for name, d in members.items() if d == dept]
                    if dept_members:
                        for member in dept_members:
                            st.write(f"- {member}")
                    else:
                        st.write("- 없음")
            else:
                st.info("등록된 동아리원이 없습니다.")
        
        elif submenu == "동아리원 추가":
            name = st.text_input("추가할 동아리원 이름")
            department = st.selectbox("부서 선택", system.departments)
            
            if st.button("추가"):
                if name:
                    success, message = system.add_member(name, department)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.warning("이름을 입력해주세요.")
        
        else:  # 동아리원 삭제
            members = system.get_members_list()
            if members:
                name = st.selectbox("삭제할 동아리원 선택", list(members.keys()))
                if st.button("삭제"):
                    if system.remove_member(name):
                        st.success(f"{name}님이 동아리원 목록에서 삭제되었습니다.")
                    else:
                        st.error(f"{name}님은 동아리원 목록에 없습니다.")
            else:
                st.info("등록된 동아리원이 없습니다.")

    elif menu == "출석 기록 수정":
        st.header("출석 기록 수정")
        
        # 날짜 선택
        selected_date = st.date_input(
            "수정할 출석 날짜를 선택하세요",
            value=datetime.now(),
            format="YYYY-MM-DD"
        )
        
        # 해당 날짜의 출석 기록 가져오기
        df = system.view_attendance(selected_date.strftime('%Y-%m-%d'))
        
        if len(df) > 0:
            # 이름 선택
            name = st.selectbox(
                "수정할 동아리원을 선택하세요",
                options=df['이름'].unique()
            )
            
            # 현재 출석 상태 표시
            current_status = df[df['이름'] == name]['출석상태'].iloc[0]
            st.write(f"현재 출석 상태: {current_status}")
            
            # 새로운 출석 상태 선택
            new_status = st.radio(
                "새로운 출석 상태를 선택하세요",
                ["출석", "지각", "결석"]
            )
            
            if st.button("출석 상태 수정"):
                success, message = system.modify_attendance(
                    selected_date.strftime('%Y-%m-%d'),
                    name,
                    new_status
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)
        else:
            st.warning(f"{selected_date.strftime('%Y-%m-%d')}에 출석 기록이 없습니다.")

if __name__ == "__main__":
    main() 