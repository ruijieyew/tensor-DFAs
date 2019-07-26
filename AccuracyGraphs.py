import matplotlib.pyplot as plt
import DfaSearchSim
import os
from statsmodels.stats.proportion import proportion_confint
import numpy as np

NUM_THRESH = 40
NUM_DFA = 100
NUM_SAMPLED = 200 # TODO rename

def run_sim():
    '''
    Wrapper function to run Monte Carlo simulation with different threshold accuracies (thresh)
    Could expand to vary more than just parameter thresh
    '''
    thresh_l = []  # list to keep track of threshold accuracy
    low_bound_l = []
    mean_l = []
    up_bound_l = []  # list of DFAs that approximate a target DFA within thresh accuracy
    
    for i in range(NUM_THRESH + 1):
        thresh = i / NUM_THRESH  # normalize to be a proportion between 0 and 1
        DfaSearchSim.Q_MIN = thresh  # set value of Q_MIN in simulation module
        thresh_l.append(thresh)
        
        temp_prop_l = []
        for j in range(NUM_DFA):
            temp_prop_l.append(DfaSearchSim.sim())
        
        
        # print marker to see progress of program
        print("--------------------------------------")
        print("	Q min  " + str(i))
        print("--------------------------------------")
    
        mu = np.mean(temp_prop_l)
        conf_int = st.t.interval(0.95, len(temp_prop_l)-1, loc=mu, scale=st.sem(temp_prop_l))
        
        low_bound_l.append(conf_int[0])
        mean_l.append(mu)
        up_bound_l.append(conf_int[1])
    
    return thresh_l, low_bound_l, mean_l, up_bound_l


def subplot_graph():
    '''
    Plot proportion of randomly-sampled DFAs that are approximately accurate for 9 different target DFA

    Right now this function is producing two different figures,
    the second of which is just the right half of the forst
    with slight modifications
    '''
    color_l = ['mediumvioletred', 'lightseagreen', 'darkgreen',
               'sandybrown', 'firebrick', 'rebeccapurple',
               'cadetblue', 'darkgoldenrod', 'indigo']

    # (1) Initialize figure with 9 subplots
    # fig, axs = plt.subplots(3, 3, sharex=True, sharey=True)

    fig, axs = plt.subplots(ncols=6, nrows=3, sharex=True, sharey=True)
    gs = axs[1, 2].get_gridspec()
    # remove the underlying axes
    for ax in axs[0:, 3]:
        ax.remove()
    for ax in axs[0:, 4]:
        ax.remove()
    for ax in axs[0:, 5]:
        ax.remove()

    axbig = fig.add_subplot(gs[0:, 3:])

    fig.tight_layout()


    # These lists are used only for the second figure
    thresh_l_l = []
    above_thresh_l_l = []
    for row in range(3): # Iterate over each subplot
        for column in range(3):

            # Initialize array to hold error bar lengths
            err = []

            # clean directory of auxilary files
            i = row*3+column
            file = "Kate_noam" + str(i) + ".txt"
            if os.path.exists(file):
                os.remove(file)
                print(file + " removed from directory")

            # Get accuracies for NUM_SAMPLED DFAs and plot the proportion of which are over each threshold accuracy
            accuracy_l = DfaSearchSim.sim2(NUM_SAMPLED)

            thresh_l = []
            above_thresh_l = []
            for i in range(NUM_THRESH + 1):
                thresh = i / NUM_THRESH
                above_thresh_acc = [acc for j, acc in enumerate(accuracy_l) if acc > thresh]
                above_thresh_prop = len(above_thresh_acc)/NUM_SAMPLED

                # fill in lists to plot
                thresh_l.append(thresh)
                above_thresh_l.append(above_thresh_prop)

                # add error
                err.append(1.96*(above_thresh_prop*(1-above_thresh_prop)/NUM_SAMPLED)**(1/2))

            axs[row, column].errorbar(thresh_l, above_thresh_l, err, c=color_l[row*3+column])

            # Used only for the second figure
            thresh_l_l.append(thresh_l)
            above_thresh_l_l.append(above_thresh_l)

    for i, thresh_l in enumerate(thresh_l_l):
        axbig.plot(thresh_l, above_thresh_l_l[i], marker='x', c=color_l[i])

    # Label axes and add title
    plt.suptitle('Proportion of Randomly-Sampled ' + str(DfaSearchSim.NUM_STATES) + '-State DFA that Approximate a Target DFA')
    axs[2,2].set_xlabel('Threshold Accuracy')
    axs[1,0].set_ylabel('Proportion of Randomly-Sampled DFA that are Approximately Accurate')
    plt.ylim([0,1])

    # (2) Create second figure with "hurricane tracking" plotting of previous data (all on top of each other)
    plt.figure()
    for i, thresh_l in enumerate(thresh_l_l):
        plt.plot(thresh_l, above_thresh_l_l[i], marker='o', c=color_l[i])

    plt.title('Spaghetti Plot (each line represents a different target DFA)')
    plt.xlabel('Threshold Accuracy')
    plt.ylabel('Proportion of Randomly-Sampled DFA that are Approximately Accurate')
    return


def general_plot():
    '''
    This is just the code we have been using in a main block. I put it in a function.
    '''

    # # UNCOMMENT IF YOU WANT 1-D HISTOGRAM OF ACTUAL ACCURACIES OF TEST DFA (PDF)
    # accuracy_l = DfaSearchSim.sim2()
    # plt.hist(accuracy_l, density=True)
    # # kde = st.gaussian_kde(accuracy_l, bw_method='silverman')
    # # plt.plot(np.linspace(0, 1, 100), kde(np.linspace(0, 1, 100)))


    # UNCOMMENT IF YOU WANT PLOT OF Q_MIN VS # TEST DFA W/ ACCURACY > Q_MIN (CDF)
    # actual plotting (this is all you really need)
    q_min_l, low_bound_l, mean_l, up_bound_l = run_sim()
    
    # plt.plot(q_min_l, low_bound_l, 'b')
    # plt.scatter(q_min_l, mean_l, 'r')
    # plt.plot(q_min_l, up_bound_l, 'b')
    error1 = [proportion_confint(mean_l[i]*DfaSearchSim.NUM_SIM, DfaSearchSim.NUM_SIM, alpha=0.05, method='normal') for i in range(NUM_THRESH+1)]
    error = [(conf_int[1] - conf_int[0])/2 for i, conf_int in enumerate(error1)]
    plt.errorbar(q_min_l, mean_l, yerr=error, fmt='o')

    # add axes labels and title
    plt.title('Proportion of Randomly-Sampled DFAs that are Approximately Accurate \n with 95% Confidence Interval')
    plt.xlabel('Threshold Accuracy') #approximately accurate threshold proportion of correctly classified DFAs
    plt.ylabel('Proportion of DFA Above Threshold')

    # # add sidebar showing the values of relevant constants
    # textstr = 'Parameters'
    # textstr2 = 'States in DFA: ' + str(DfaSearchSim.NUM_STATES) + ' \n' + \
    #           'Cardinality of alphabet: ' + str(DfaSearchSim.NUM_SYM) + ' \n' + \
    #           'Test strings: ' + str(DfaSearchSim.NUM_EXAMPLES) + ' \n' + \
    #           'Test string length: ' + str(DfaSearchSim.STR_LENGTH) + ' \n' + \
    #           'Number of test DFAs: ' + str(DfaSearchSim.NUM_SIM) + ' \n' + \
    #           'Simulations per threshold accuracy: ' + str(NUM_DFA)
    #           # 'Points per q_min: ' + str(NUM_DFA) + ' \n' + \
    #           # 'Number of q_min tested: ' + str(NUM_THRESH) + ' \n' + \
    #           # 'Number of simulations per graph point: ' + str(DfaSearchSim.NUM_SIM)
    # plt.text(0.92, 0.8, textstr, fontsize=14, fontweight='bold', transform=plt.gcf().transFigure)
    # plt.text(0.92, .3, textstr2, fontsize=14, transform=plt.gcf().transFigure)


    # # THIS IS KYLE'S CODE. IT IS NOT COMPATIBLE WITH THE CURRENT run_sim FUNCTION
    # plt.figure(1)
    # plt.scatter(individual_dis[20][0], individual_dis[20][1])
    # plt.title('distribution for a specific q_min')
    # plt.xlabel('q_min') #approximately accurate threshold proportion of correctly classified DFAs
    # plt.ylabel('approximately accurate proportion')
    # plt.show()


    # # JUST NEVER UNCOMMENT THIS. :)
    # plt.figure(figsize = (10, 4.8))
    # i = 1
    # while i != -1:
    # 	print(listdir())
    # 	if 'dfaGraph' + str(i) + '.jpg' not in listdir():
    # 		plt.savefig('dfaGraph'+ str(i)+ '.jpg')
    # 		i = -1
    # 	else: i += 1
