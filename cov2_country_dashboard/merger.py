#!/usr/bin/env python3.8

# Copyright [2020] EMBL-European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pandas as pd
class Merger:
    def __init__(self, data, database, GCA_data=pd.DataFrame()):
        self.data = data
        self.database = database
        self.GCA_data = GCA_data

    def __getitem__(self, index):
        return self.final_merge()[index]



    def final_merge(self):

        project_grouped = self.table_merger()[1]
        sample_grouped = self.table_merger()[2]
        project_status_grouped = self.total_status_grouping(self.data, 'project')
        sample_status_grouped = self.total_status_grouping(self.data, 'sample')
        sample_status_merge = self.status_table_merge(sample_status_grouped[0], sample_status_grouped[1],
                                                 sample_status_grouped[2], sample_status_grouped[3],
                                                 ['Webin Account', 'Project ID', 'Country'])

        center_name_grouped = self.grouping(self.data,['Webin Account', 'Project ID', 'Country', 'Center Name'], 'Centers Counts')
        center_name_final = center_name_grouped.drop(columns='Centers Counts')

        # For project
        webin_project_grouped = self.grouping(project_grouped, ['Webin Account', 'Country'],
                                         'Project')  # 'Total Project Counts in each Webin'
        # For Samples
        webin_sample_grouped = self.grouping(sample_grouped, ['Webin Account', 'Country'],
                                        'Samples')  # 'Sample Counts in each Webin
        project_sample_grouped = self.grouping(sample_grouped,
                                          ['Webin Account', 'Project ID', 'Project Status ID', 'Country'],
                                          'Samples')  # Sample Counts in each Project
        project_status_merge = self.status_table_merge(project_status_grouped[0], project_status_grouped[1],
                                                       project_status_grouped[2], project_status_grouped[3],
                                                       ['Webin Account', 'Country'])
        ##### Table 1 merger #####
        # status merge

        # table merge
        if self.database == 'reads':
            webin_run_grouped = self.table_merger()[0]
            webin_experiment_grouped = self.table_merger()[3]
            project_experiment_grouped = self.table_merger()[4]
            ex_status_merge = self.table_merger()[5]
            webin_count_merge_final = self.count_table_merge(['Webin Account', 'Country'],webin_project_grouped, project_status_merge, webin_sample_grouped, webin_run_grouped,webin_experiment_grouped).fillna(0).replace('', 0)

            project_count_merge_final = self.count_table_merge(['Webin Account', 'Project ID', 'Country'], project_sample_grouped, sample_status_merge,
                                                          project_experiment_grouped, ex_status_merge).fillna(0).replace('', 0)

        else:
            webin_analysis_grouped = self.table_merger()[0]
            analysis_status_merge = self.table_merger()[3]
            webin_GCA_grouped = self.table_merger()[4]
            project_GCA_grouped = self.table_merger()[5]
            project_analysis_grouped = self.table_merger()[6]
            webin_count_merge_final = self.count_table_merge(['Webin Account', 'Country'], webin_project_grouped, project_status_merge, webin_sample_grouped, webin_analysis_grouped,webin_GCA_grouped).fillna(0).replace('', 0)

            project_count_merge_final = self.count_table_merge(['Webin Account', 'Project ID', 'Country'],
                                                               project_sample_grouped, sample_status_merge,project_analysis_grouped,
                                                               analysis_status_merge,project_GCA_grouped).fillna(0).replace('', 0)

        return webin_count_merge_final, project_count_merge_final, center_name_final



    def table_merger (self):

        if self.database == 'reads':
            # For runs
            webin_run_grouped = self.grouping(self.data, ['Webin Account', 'Country'], 'Runs')  # Total run Counts in each Webin
            # For project
            project_grouped = self.grouping(self.data, ['Webin Account', 'Project ID', 'Country'], 'Runs')  # 'Total run Counts in each Project'
            # For Samples
            sample_grouped = self.grouping(self.data,
                                          ['Webin Account', 'Project ID','Project Status ID','Sample ID', 'Country'],
                                          'Runs')  # RUN ID Counts in each Sample
            # For Experiments
            experiment_grouped = self.grouping(self.data, ['Webin Account', 'Project ID', 'Sample ID', 'RUN ID', 'Country'],
                                          'Experiment ID Counts')
            webin_experiment_grouped = self.grouping(experiment_grouped, ['Webin Account', 'Country'],
                                                'Experiments')  # 'Experiment ID Counts in each Webin'
            project_experiment_grouped = self.grouping(experiment_grouped, ['Webin Account', 'Project ID', 'Country'],
                                                  'Experiments')  # experiment Counts in each Project
            ex_status_grouped = self.total_status_grouping(self.data, 'experiment')
            ex_status_merge = self.status_table_merge(ex_status_grouped[0], ex_status_grouped[1], ex_status_grouped[2],
                                                 ex_status_grouped[3], ['Webin Account', 'Project ID', 'Country'])
            return  webin_run_grouped, project_grouped, sample_grouped, webin_experiment_grouped, project_experiment_grouped, ex_status_merge

        else:
            #for Analysis
            project_grouped = self.grouping(self.data, ['Webin Account', 'Project ID', 'Country'], 'Project ID counts')  # 'Total project Counts in each webin'
            sample_grouped = self.grouping(self.data,
                                           ['Webin Account', 'Project ID','Project Status ID', 'Sample ID', 'Country'], 'Sample ID counts') # 'Total samples Counts in each webin'

            analysis_grouped = self.grouping(self.data,
                                               ['Webin Account', 'Project ID', 'Sample ID', 'Country'],  'Analysis ID')

            webin_analysis_grouped = self.grouping(analysis_grouped, ['Webin Account', 'Country'], 'Analysis ID')  # Total analysis Counts in each Webin

            GCA_webin_grouped = self.grouping(self.GCA_data,
                                               ['Webin Account', 'Project ID', 'Sample ID', 'Country'],
                                               'GCA ID Counts')

            webin_GCA_grouped = self.grouping(GCA_webin_grouped, ['Webin Account', 'Country'],
                                                   'GCA ID')  # Total GCA Counts in each project


            project_GCA_grouped = self.grouping(GCA_webin_grouped, ['Webin Account', 'Project ID', 'Country'],
                                              'GCA ID')  # Total GCA Counts in each project



            # For project

            project_analysis_grouped = self.grouping(analysis_grouped, ['Webin Account','Project ID', 'Country'], 'Analysis ID')
            # For Samples
            #sample_grouped = self.grouping(self.data,
                                          #['Webin Account', 'Project ID', 'Sample ID', 'Country'],
                                          #'Analysis ID')  # Analysis ID Counts in each Sample
            analysis_status_grouped = self.total_status_grouping(self.data, 'analysis')
            analysis_status_merge = self.status_table_merge(analysis_status_grouped[0], analysis_status_grouped[1],
                                                            analysis_status_grouped[2],
                                                            analysis_status_grouped[3],
                                                            ['Webin Account', 'Project ID', 'Country'])
            return webin_analysis_grouped, project_grouped, sample_grouped, analysis_status_merge, webin_GCA_grouped, project_GCA_grouped, project_analysis_grouped



    def grouping(self,df,column_names,resulted_column):
        grouped = df.groupby(column_names).size().reset_index(name=resulted_column)
        return grouped




    def status_grouping (self, df, main_column_names, main_resulted_column, status_column_name, status_id, final_column_names, final_resulted_column):
        try:
            status_grouped_main = self.grouping(df, main_column_names, main_resulted_column)
            status_grouped = status_grouped_main.groupby(status_column_name).get_group(status_id)
            status_grouped_final = self.grouping(status_grouped, final_column_names, final_resulted_column)
            return status_grouped_final

        except KeyError:
            status_grouped_final = pd.DataFrame()
            return status_grouped_final
            pass


    def total_status_grouping(self, df, object_type):

        if object_type == 'project':
            main_column_name = ['Webin Account','Project ID','Project Status ID','Country']
            main_resulted_column = 'project in each webin'
            status_column_name = 'Project Status ID'
            final_column_names = ['Webin Account','Country']
            object = 'Project'

        elif object_type == 'sample':
            main_column_name = ['Webin Account','Project ID','Sample ID','Sample Status ID','Country']
            main_resulted_column = 'sample in each webin'
            status_column_name = 'Sample Status ID'
            final_column_names = ['Webin Account','Project ID','Country']
            object = 'Sample'

        elif object_type == 'experiment':
            main_column_name = ['Webin Account','Project ID','Sample ID','Sample Status ID','experiment_accession','Experiment Status ID','Country']
            main_resulted_column = 'experiment in each webin'
            status_column_name = 'Experiment Status ID'
            final_column_names = ['Webin Account','Project ID','Country']
            object = 'Experiments'

        elif object_type == 'analysis':
            main_column_name = ['Webin Account','Project ID','Sample ID','Sample Status ID','Analysis ID','Analysis Status ID','Country']
            main_resulted_column = 'analysis in each webin'
            status_column_name = 'Analysis Status ID'
            final_column_names = ['Webin Account','Project ID','Country']
            object = 'Analysis'

        elif object_type == 'sequence':
            main_column_name = ['Webin Account','Project ID','Sample ID','Sample Status ID','accession','Analysis Status ID','Country']
            main_resulted_column = 'sequence in each webin'
            status_column_name = 'Sequence Status ID'
            final_column_names = ['Webin Account','Project ID','Country']
            object = 'Sequences'



        status_grouped_private = self.status_grouping(df,main_column_name,main_resulted_column,status_column_name, '2' ,final_column_names,f'Private {object}')

        status_grouped_public = self.status_grouping(df,main_column_name,main_resulted_column,status_column_name, '4' ,final_column_names,f'Public {object}')

        status_grouped_suppressed = self.status_grouping(df,main_column_name,main_resulted_column,status_column_name, '5' ,final_column_names,f'Suppressed {object}')

        status_grouped_canceled = self.status_grouping(df,main_column_name,main_resulted_column,status_column_name, '3' ,final_column_names,f'Cancelled {object}')

        return status_grouped_private, status_grouped_public, status_grouped_suppressed, status_grouped_canceled


    def status_table_merge(self, df1,df2,df3,df4,column_names):
        try:
            status_merge1=pd.merge(df1, df2, on=column_names, how='outer')
        except KeyError:
            if df1.empty:
                status_merge1 = df2
            elif df2.empty:
                status_merge1 = df1
            else:
                status_merge1 = pd.DataFrame(columns = column_names)
        try:
           status_merge2=pd.merge(status_merge1, df3, on=column_names, how='outer')

        except KeyError:
            if df3.empty:
                status_merge2 = status_merge1
            else:
                status_merge2 = pd.DataFrame(columns=column_names)

        try:
            status_merge = pd.merge(status_merge2, df4, on=column_names, how='outer')
            return status_merge
        except KeyError:
            if df4.empty:
                status_merge = status_merge2
            else:
                status_merge = pd.DataFrame(columns=column_names)

            return status_merge


    def count_table_merge (self, column_names,df1,df2,df3,df4=pd.DataFrame(),df5=pd.DataFrame()):
        count_merge1 = pd.merge(df1, df2,
                                        on=column_names, how='outer')
        count_merge2 = pd.merge(count_merge1, df3,
                                        on=column_names, how='outer')
        if df4.empty:
            count_merge_final = count_merge2

        elif not df4.empty and df5.empty:
            count_merge_final = pd.merge(count_merge2, df4,
                                                 on=column_names, how='outer')
        else:
            count_merge3 =  pd.merge(count_merge2, df4,
                                        on=column_names, how='outer')
            count_merge_final = pd.merge(count_merge3, df5,
                                         on=column_names, how='outer')

        return count_merge_final