##########################################################
#### Template Written By: H2O Wave                    ####
#### Enhanced with Streaming Data By: Satyaki De      ####
#### Base Version Enhancement On: 20-Dec-2020         ####
#### Modified On 26-Dec-2020                          ####
####                                                  ####
#### Objective: This script will consume real-time    ####
#### streaming data coming out from a hosted API      ####
#### sources using another popular third-party        ####
#### service named Ably. Ably mimics pubsub Streaming ####
#### concept, which might be extremely useful for     ####
#### any start-ups.                                   ####
##########################################################

import time
from h2o_wave import site, data, ui
from ably import AblyRest
import pandas as p
import json

class DaSeries:
    def __init__(self, inputDf):
        self.Df = inputDf
        self.count_row = inputDf.shape[0]
        self.start_pos = 0
        self.end_pos = 0
        self.interval = 1


    def next(self):
        try:
            # Getting Individual Element & convert them to Series
            if ((self.start_pos + self.interval) <= self.count_row):
                self.end_pos = self.start_pos + self.interval
            else:
                self.end_pos = self.start_pos + (self.count_row - self.start_pos)

            split_df = self.Df.iloc[self.start_pos:self.end_pos]

            if ((self.start_pos > self.count_row) | (self.start_pos == self.count_row)):
                pass
            else:
                self.start_pos = self.start_pos + self.interval

            x = float(split_df.iloc[0]['CurrentExchange'])
            dx = float(split_df.iloc[0]['Change'])

            # Emptying the exisitng dataframe
            split_df = p.DataFrame(None)

            return x, dx
        except:
            x = 0
            dx = 0

            return x, dx

class CategoricalSeries:
    def __init__(self, sourceDf):
        self.series = DaSeries(sourceDf)
        self.i = 0

    def next(self):
        x, dx = self.series.next()
        self.i += 1
        return f'C{self.i}', x, dx


light_theme_colors = '$red $pink $purple $violet $indigo $blue $azure $cyan $teal $mint $green $amber $orange $tangerine'.split()
dark_theme_colors = '$red $pink $blue $azure $cyan $teal $mint $green $lime $yellow $amber $orange $tangerine'.split()

_color_index = -1
colors = dark_theme_colors

def next_color():
    global _color_index
    _color_index += 1
    return colors[_color_index % len(colors)]


_curve_index = -1
curves = 'linear smooth step stepAfter stepBefore'.split()


def next_curve():
    global _curve_index
    _curve_index += 1
    return curves[_curve_index % len(curves)]


def create_dashboard(update_freq=0.0):
    page = site['/dashboard_st']

    # Fetching the data
    client = AblyRest('EPfR2A.6DWu7g:lBd3Z6IC39pceflE')
    channel = client.channels.get('sd_channel')

    message_page = channel.history()

    # Counter Value
    cnt = 0

    # Declaring Global Data-Frame
    df_conv = p.DataFrame()

    for i in message_page.items:
        print('Last Msg: {}'.format(i.data))
        json_data = json.loads(i.data)

        # Converting JSON to Dataframe
        df = p.json_normalize(json_data)
        df.columns = df.columns.map(lambda x: x.split(".")[-1])

        if cnt == 0:
            df_conv = df
        else:
            d_frames = [df_conv, df]
            df_conv = p.concat(d_frames)

        cnt += 1

    # Resetting the Index Value
    df_conv.reset_index(drop=True, inplace=True)

    print('DF:')
    print(df_conv)

    #df_conv['default_rank'] = df_conv['Currency'].rank(method='first')
    #df_conv['default_rank'] = df_conv.groupby(['Currency','CurrentExchange']).cumcount() + 1
    df_conv['default_rank'] = df_conv.groupby(['Currency']).cumcount() + 1
    lkp_rank = 1
    df_unique = df_conv[(df_conv['default_rank'] == lkp_rank)]

    print('Rank DF Unique:')
    print(df_unique)

    count_row = df_unique.shape[0]

    large_lines = []
    start_pos = 0
    end_pos = 0
    interval = 1

    # Converting dataframe to a desired Series
    f = CategoricalSeries(df_conv)

    for j in range(count_row):
        # Getting the series values from above
        cat, val, pc = f.next()

        # Getting Individual Element & convert them to Series
        if ((start_pos + interval) <= count_row):
            end_pos = start_pos + interval
        else:
            end_pos = start_pos + (count_row - start_pos)

        split_df = df_unique.iloc[start_pos:end_pos]

        if ((start_pos > count_row) | (start_pos == count_row)):
            pass
        else:
            start_pos = start_pos + interval

        x_currency = str(split_df.iloc[0]['Currency'])

        ####################################################
        ##### Debug Purpose                        #########
        ####################################################
        print('Currency: ', x_currency)
        print('J: ', str(j))
        print('Cat: ', cat)
        ####################################################
        #####   End Of Debug                         #######
        ####################################################

        c = page.add(f'e{j+1}', ui.tall_series_stat_card(
            box=f'{j+1} 1 1 2',
            title=x_currency,
            value='=${{intl qux minimum_fraction_digits=2 maximum_fraction_digits=2}}',
            aux_value='={{intl quux style="percent" minimum_fraction_digits=1 maximum_fraction_digits=1}}',
            data=dict(qux=val, quux=pc),
            plot_type='area',
            plot_category='foo',
            plot_value='qux',
            plot_color=next_color(),
            plot_data=data('foo qux', -15),
            plot_zero_value=0,
            plot_curve=next_curve(),
        ))
        large_lines.append((f, c))

    page.save()

    while update_freq > 0:

        time.sleep(update_freq)

        for f, c in large_lines:
            cat, val, pc = f.next()

            print('Update Cat: ', cat)
            print('Update Val: ', val)
            print('Update pc: ', pc)
            print('*' * 160)

            c.data.qux = val
            c.data.quux = pc / 100
            c.plot_data[-1] = [cat, val]

        page.save()

create_dashboard(update_freq=0.25)
